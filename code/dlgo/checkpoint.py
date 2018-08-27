from __future__ import absolute_import
import os

import h5py
from keras.models import Sequential
from keras.optimizers import Adadelta
from keras.layers.core import Dense, Activation

from dlgo import kerasutil


__all__ = [
    'TrainingRun',
]


class TrainingRun:

    def __init__(self, filename, model, epochs_completed, chunks_completed, num_chunks):
        self.filename = filename
        self.model = model
        self.epochs_completed = epochs_completed
        self.chunks_completed = chunks_completed
        self.num_chunks = num_chunks

    def save(self):
        # Backup the original file in case something goes wrong while
        # saving the new checkpoint.
        backup = None
        if os.path.exists(self.filename):
            backup = self.filename + '.bak'
            os.rename(self.filename, backup)

        output = h5py.File(self.filename, 'w')
        model_out = output.create_group('model')
        kerasutil.save_model_to_hdf5_group(self.model, model_out)
        metadata = output.create_group('metadata')
        metadata.attrs['epochs_completed'] = self.epochs_completed
        metadata.attrs['chunks_completed'] = self.chunks_completed
        metadata.attrs['num_chunks'] = self.num_chunks
        output.close()

        # If we got here, we no longer need the backup.
        if backup is not None:
            os.unlink(backup)

    def complete_chunk(self):
        self.chunks_completed += 1
        if self.chunks_completed == self.num_chunks:
            self.epochs_completed += 1
            self.chunks_completed = 0
        self.save()

    @classmethod
    def load(cls, filename):
        inp = h5py.File(filename, 'r')
        model = kerasutil.load_model_from_hdf5_group(inp['model'])
        training_run = cls(filename,
                           model,
                           inp['metadata'].attrs['epochs_completed'],
                           inp['metadata'].attrs['chunks_completed'],
                           inp['metadata'].attrs['num_chunks'])
        inp.close()
        return training_run

    @classmethod
    def create(cls, filename, index, layer_fn):
        model = Sequential()
        for layer in layer_fn((7, 19, 19)):
            model.add(layer)
        model.add(Dense(19 * 19))
        model.add(Activation('softmax'))
        opt = Adadelta(clipnorm=0.25)
        model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
        training_run = cls(filename, model, 0, 0, index.num_chunks)
        training_run.save()
        return training_run
