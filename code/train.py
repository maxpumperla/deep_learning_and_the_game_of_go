import argparse
import importlib
import multiprocessing
import os
import signal
import sys
import time

import numpy as np
import six.moves.queue as queue

from dlgo.corpora import build_index, load_index, store_index
from dlgo.encoders.betago import BetaGoEncoder
from dlgo.checkpoint import TrainingRun


def index(args):
    corpus_index = build_index(args.data, args.chunk_size)
    store_index(corpus_index, open(args.output, 'w'))


def show(args):
    corpus_index = load_index(open(args.file))
    print("Index contains %d chunks in %d physical files" % (
        corpus_index.num_chunks, len(corpus_index.physical_files)))


def _load_module_from_filename(filename):
    if sys.version_info < (3, 3):
        import imp
        return imp.load_source('dynamicmodule', filename)
    elif sys.version_info < (3, 5):
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader('dynamicmodule', filename).load_module()
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location('dynamicmodule', filename)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod


def _load_network_by_name(name):
    mod = None
    if os.path.exists(name):
        mod = _load_module_from_filename(name)
    else:
        try:
            mod = importlib.import_module('dlgo.' + name)
        except ImportError:
            mod = importlib.import_module(name)
    if not hasattr(mod, 'layers'):
        raise ImportError('%s does not defined a layers function.' % (name,))
    return mod.layers


def init(args):
    corpus_index = load_index(open(args.index))
    layer_fn = _load_network_by_name(args.network)
    TrainingRun.create(args.progress, corpus_index, layer_fn)


def _disable_keyboard_interrupt():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def _prepare_training_data_single_process(worker_idx, chunk, corpus_index, output_q, stop_q):
    # Make sure ^C gets handled in the main process.
    _disable_keyboard_interrupt()
    processor = BetaGoEncoder(board_size=(19, 19))

    chunk = corpus_index.get_chunk(chunk)
    xs, ys = [], []
    for board, next_color, next_move in chunk:
        if not stop_q.empty():
            print("Got stop signal, aborting.")
            return

        # TODO: old interface
        feature, label = processor.feature_and_label(next_color, next_move, board,
                                                     processor.num_planes)
        xs.append(feature)
        ys.append(label)
    X = np.array(xs)
    # one-hot encode the moves
    nb_classes = 19 * 19
    Y = np.zeros((len(ys), nb_classes))
    for i, y in enumerate(ys):
        Y[i][y] = 1
    output_q.put((worker_idx, X, Y))
    output_q.close()


def prepare_training_data(num_workers, next_chunk, corpus_index, output_q, stop_q):
    # Make sure ^C gets handled in the main process.
    _disable_keyboard_interrupt()
    stopped = False

    while True:
        if not stop_q.empty():
            output_q.close()
            output_q.join_thread()
            stop_q.close()
            stop_q.join_thread()
            return
        chunks_to_process = []
        for _ in range(num_workers):
            chunks_to_process.append(next_chunk)
            next_chunk = (next_chunk + 1) % corpus_index.num_chunks
        workers = []
        inter_q = multiprocessing.Queue()
        for i, chunk in enumerate(chunks_to_process):
            workers.append(multiprocessing.Process(
                target=_prepare_training_data_single_process,
                args=(i, chunk, corpus_index, inter_q, stop_q)))
        for worker in workers:
            worker.start()
        results = []
        while len(results) < len(workers):
            try:
                results.append(inter_q.get(block=True, timeout=1))
            except queue.Empty:
                if not stop_q.empty():
                    stopped = True
                    break
        for worker in workers:
            worker.join()
        inter_q.close()
        inter_q.join_thread()
        if stopped:
            output_q.close()
            return
        assert len(results) == len(workers)
        results.sort()
        for _, X, Y in results:
            output_q.put((X, Y))


def train(args):
    corpus_index = load_index(open(args.index))
    print("Index contains %d chunks in %d physical files" % (
        corpus_index.num_chunks, len(corpus_index.physical_files)))
    if not os.path.exists(args.progress):
        print('%s does not exist. Run train.py init first.' % (args.progress,))
    else:
        run = TrainingRun.load(args.progress)

    q = multiprocessing.Queue(maxsize=2 * args.workers)
    stop_q = multiprocessing.Queue()
    p = multiprocessing.Process(target=prepare_training_data,
                                args=(args.workers, run.chunks_completed, corpus_index, q, stop_q))
    p.start()
    try:
        while True:
            print("Waiting for prepared training chunk...")
            wait_start_ts = time.time()
            X, Y = q.get()
            wait_end_ts = time.time()
            print("Idle %.1f seconds" % (wait_end_ts - wait_start_ts,))
            print("Training epoch %d chunk %d/%d..." % (
                run.epochs_completed + 1,
                run.chunks_completed + 1,
                run.num_chunks))
            run.model.fit(X, Y, epochs=1)
            run.complete_chunk()
    finally:
        # Drain the receive queue.
        while not q.empty():
            q.get()
        q.close()
        q.join_thread()
        print("Shutting down workers, please wait...")
        stop_q.put(1)
        stop_q.close()
        p.join()


def export(args):
    run = TrainingRun.load(args.progress)

    model_file = args.bot + '_bot.yml'
    weight_file = args.bot + '_weights.hd5'
    run.model.save_weights(weight_file, overwrite=True)
    with open(model_file, 'w') as yml:
        yml.write(run.model.to_yaml())


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    index_parser = subparsers.add_parser('index', help='Build an index for a corpus.')
    index_parser.set_defaults(command='index')
    index_parser.add_argument('--output', '-o', required=True,
                              help='Path to store the index.')
    index_parser.add_argument('--data', '-d', required=True,
                              help='Directory or archive containing SGF files.')
    index_parser.add_argument('--chunk-size', '-c', type=int, default=20000,
                              help='Number of examples per training chunk.')

    show_parser = subparsers.add_parser('show', help='Show a summary of an index.')
    show_parser.set_defaults(command='show')
    show_parser.add_argument('--file', '-f', required=True, help='Index file.')

    init_parser = subparsers.add_parser('init', help='Start training.')
    init_parser.set_defaults(command='init')
    init_parser.add_argument('--index', '-i', required=True, help='Index file.')
    init_parser.add_argument('--progress', '-p', required=True, help='Progress file.')
    init_parser.add_argument('--network', '-n', required=True,
                             help='Python module that defines the network architecture, '
                                  'e.g. "networks.small"')

    train_parser = subparsers.add_parser('train', help='Do some training.')
    train_parser.set_defaults(command='train')
    train_parser.add_argument('--index', '-i', required=True, help='Index file.')
    train_parser.add_argument('--progress', '-p', required=True, help='Progress file.')
    train_parser.add_argument('--workers', '-w', type=int, default=1,
                              help='Number of workers to use for preprocessing boards.')

    export_parser = subparsers.add_parser('export', help='Export a bot from a training run.')
    export_parser.set_defaults(command='export')
    export_parser.add_argument('--progress', '-p', required=True, help='Progress file.')
    export_parser.add_argument('--bot', '-b', help='Bot file name.')

    args = parser.parse_args()

    if args.command == 'index':
        index(args)
    elif args.command == 'show':
        show(args)
    elif args.command == 'init':
        init(args)
    elif args.command == 'train':
        train(args)
    elif args.command == 'export':
        export(args)


if __name__ == '__main__':
    main()
