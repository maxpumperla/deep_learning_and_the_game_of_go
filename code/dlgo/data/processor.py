from __future__ import absolute_import

# tag::base_imports[]
import os.path
import tarfile
import gzip
import glob
import shutil

import numpy as np
from keras.utils import to_categorical
# end::base_imports[]

# tag::dlgo_imports[]
from dlgo.gosgf import Sgf_game
from dlgo.goboard_fast import Board, GameState, Move
from dlgo.gotypes import Player, Point
from dlgo.encoders.base import get_encoder_by_name

from dlgo.data.index_processor import KGSIndex
from dlgo.data.sampling import Sampler  # <1>
# <1> Sampler will be used to sample training and test data from files.
# end::dlgo_imports[]


# tag::processor_init[]
class GoDataProcessor:
    def __init__(self, encoder='oneplane', data_directory='data'):
        self.encoder = get_encoder_by_name(encoder, 19)
        self.data_dir = data_directory
# end::processor_init[]

# tag::load_go_data[]
    def load_go_data(self, data_type='train',  # <1>
                     num_samples=1000):  # <2>
        index = KGSIndex(data_directory=self.data_dir)
        index.download_files()  # <3>

        sampler = Sampler(data_dir=self.data_dir)
        data = sampler.draw_data(data_type, num_samples)  # <4>

        zip_names = set()
        indices_by_zip_name = {}
        for filename, index in data:
            zip_names.add(filename)  # <5>
            if filename not in indices_by_zip_name:
                indices_by_zip_name[filename] = []
            indices_by_zip_name[filename].append(index)  # <6>
        for zip_name in zip_names:
            base_name = zip_name.replace('.tar.gz', '')
            data_file_name = base_name + data_type
            if not os.path.isfile(self.data_dir + '/' + data_file_name):
                self.process_zip(zip_name, data_file_name, indices_by_zip_name[zip_name])  # <7>

        features_and_labels = self.consolidate_games(data_type, data)  # <8>
        return features_and_labels

# <1> As `data_type` you can choose either 'train' or 'test'.
# <2> `num_samples` refers to the number of games to load data from.
# <3> We download all games from KGS to our local data directory. If data is available, it won't be downloaded again.
# <4> The `Sampler` instance selects the specified number of games for a data type.
# <5> We collect all zip file names contained in the data in a list.
# <6> Then we group all SGF file indices by zip file name.
# <7> The zip files are then processed individually.
# <8> Features and labels from each zip are then aggregated and returned.
# end::load_go_data[]

# tag::unzip_data[]
    def unzip_data(self, zip_file_name):
        this_gz = gzip.open(self.data_dir + '/' + zip_file_name)  # <1>

        tar_file = zip_file_name[0:-3]  # <2>
        this_tar = open(self.data_dir + '/' + tar_file, 'wb')

        shutil.copyfileobj(this_gz, this_tar)  # <3>
        this_tar.close()
        return tar_file

# <1> Unpack the `gz` file into a `tar` file.
# <2> Remove ".gz" at the end to get the name of the tar file.
# <3> Copy the contents of the unpacked file into the `tar` file.
# end::unzip_data[]

# tag::read_sgf_files[]
    def process_zip(self, zip_file_name, data_file_name, game_list):
        tar_file = self.unzip_data(zip_file_name)
        zip_file = tarfile.open(self.data_dir + '/' + tar_file)
        name_list = zip_file.getnames()
        total_examples = self.num_total_examples(zip_file, game_list, name_list)  # <1>

        shape = self.encoder.shape()  # <2>
        feature_shape = np.insert(shape, 0, np.asarray([total_examples]))
        features = np.zeros(feature_shape)
        labels = np.zeros((total_examples,))

        counter = 0
        for index in game_list:
            name = name_list[index + 1]
            if not name.endswith('.sgf'):
                raise ValueError(name + ' is not a valid sgf')
            sgf_content = zip_file.extractfile(name).read()
            sgf = Sgf_game.from_string(sgf_content)  # <3>

            game_state, first_move_done = self.get_handicap(sgf)  # <4>

            for item in sgf.main_sequence_iter():  # <5>
                color, move_tuple = item.get_move()
                point = None
                if color is not None:
                    if move_tuple is not None:  # <6>
                        row, col = move_tuple
                        point = Point(row + 1, col + 1)
                        move = Move.play(point)
                    else:
                        move = Move.pass_turn()  # <7>
                    if first_move_done and point is not None:
                        features[counter] = self.encoder.encode(game_state)  # <8>
                        labels[counter] = self.encoder.encode_point(point)  # <9>
                        counter += 1
                    game_state = game_state.apply_move(move)  # <10>
                    first_move_done = True
# <1> Determine the total number of moves in all games in this zip file.
# <2> Infer the shape of features and labels from the encoder we use.
# <3> Read the SGF content as string, after extracting the zip file.
# <4> Infer the initial game state by applying all handicap stones.
# <5> Iterate over all moves in the SGF file.
# <6> Read the coordinates of the stone to be played...
# <7> ... or pass, if there is none.
# <8> We encode the current game state as features...
# <9> ... and the next move as label for the features.
# <10> Afterwards the move is applied to the board and we proceed with the next one.
# end::read_sgf_files[]

# tag::store_features_and_labels[]
        feature_file_base = self.data_dir + '/' + data_file_name + '_features_%d'
        label_file_base = self.data_dir + '/' + data_file_name + '_labels_%d'

        chunk = 0  # Due to files with large content, split up after chunksize
        chunksize = 1024
        while features.shape[0] >= chunksize:  # <1>
            feature_file = feature_file_base % chunk
            label_file = label_file_base % chunk
            chunk += 1
            current_features, features = features[:chunksize], features[chunksize:]
            current_labels, labels = labels[:chunksize], labels[chunksize:]  # <2>
            np.save(feature_file, current_features)
            np.save(label_file, current_labels)  # <3>
# <1> We process features and labels in chunks of size 1024.
# <2> The current chunk is cut off from features and labels...
# <3> ...  and then stored in a separate file.
# end::store_features_and_labels[]

# tag::consolidate_games[]
    def consolidate_games(self, data_type, samples):
        files_needed = set(file_name for file_name, index in samples)
        file_names = []
        for zip_file_name in files_needed:
            file_name = zip_file_name.replace('.tar.gz', '') + data_type
            file_names.append(file_name)

        feature_list = []
        label_list = []
        for file_name in file_names:
            file_prefix = file_name.replace('.tar.gz', '')
            base = self.data_dir + '/' + file_prefix + '_features_*.npy'
            for feature_file in glob.glob(base):
                label_file = feature_file.replace('features', 'labels')
                x = np.load(feature_file)
                y = np.load(label_file)
                x = x.astype('float32')
                y = to_categorical(y.astype(int), 19 * 19)
                feature_list.append(x)
                label_list.append(y)
        features = np.concatenate(feature_list, axis=0)
        labels = np.concatenate(label_list, axis=0)
        np.save('{}/features_{}.npy'.format(self.data_dir, data_type), features)
        np.save('{}/labels_{}.npy'.format(self.data_dir, data_type), labels)

        return features, labels
# end::consolidate_games[]

# tag::get_handicap[]
    @staticmethod
    def get_handicap(sgf):
        go_board = Board(19, 19)
        first_move_done = False
        move = None
        game_state = GameState.new_game(19)
        if sgf.get_handicap() is not None and sgf.get_handicap() != 0:
            for setup in sgf.get_root().get_setup_stones():
                for move in setup:
                    row, col = move
                    go_board.place_stone(Player.black, Point(row + 1, col + 1))
            first_move_done = True
            game_state = GameState(go_board, Player.white, None, move)
        return game_state, first_move_done
# end::get_handicap[]

# tag::num_total_examples[]
    def num_total_examples(self, zip_file, game_list, name_list):
        total_examples = 0
        for index in game_list:
            name = name_list[index + 1]
            if name.endswith('.sgf'):
                sgf_content = zip_file.extractfile(name).read()
                sgf = Sgf_game.from_string(sgf_content)
                game_state, first_move_done = self.get_handicap(sgf)

                num_moves = 0
                for item in sgf.main_sequence_iter():
                    color, move = item.get_move()
                    if color is not None:
                        if first_move_done:
                            num_moves += 1
                        first_move_done = True
                total_examples = total_examples + num_moves
            else:
                raise ValueError(name + ' is not a valid sgf')
        return total_examples
# end::num_total_examples[]
