# tag::data_generator[]
import gc  # <1>
import glob
import numpy as np
from keras.utils import to_categorical


class DataGenerator(object):
    def __init__(self, data_directory, samples):
        self.data_directory = data_directory
        self.samples = samples
        self.files = set(file_name for file_name, index in samples)  # <2>
        self.num_samples = None

    def get_num_samples(self, batch_size=128, num_classes=19 * 19):  # <3>
        if self.num_samples is not None:
            return self.num_samples
        else:
            self.num_samples = 0
            for X, y in self._generate(batch_size=batch_size, num_classes=num_classes):
                self.num_samples += X.shape[0]
            return self.num_samples
# <1> We use a garbage collector (gc) to free up memory from unused structures.
# <2> Our generator has access to a set of files that we sampled earlier.
# <3> Depending on the application, we may need to know how many examples we have.
# end::data_generator[]

# tag::private_generate[]
    def _generate(self, batch_size, num_classes):
        for zip_file_name in self.files:
            file_name = zip_file_name.replace('.tar.gz', '') + 'train'
            base = self.data_directory + '/' + file_name + '_features_*.npy'
            for feature_file in glob.glob(base):
                label_file = feature_file.replace('features', 'labels')
                X = np.load(feature_file)
                y = np.load(label_file)
                X = X.astype('float32')
                y = to_categorical(y.astype(int), num_classes)
                gc.collect()
                while X.shape[0] >= batch_size:
                    X_batch, X = X[:batch_size], X[batch_size:]
                    y_batch, y = y[:batch_size], y[batch_size:]
                    gc.collect()
                    yield X_batch, y_batch  # <1>
            gc.collect()

# <1> We yield batches of data as we go.
# end::private_generate[]

# tag::generate[]
    def generate(self, batch_size=128, num_classes=19 * 19):
        while True:
            for item in self._generate(batch_size, num_classes):
                yield item
# end::generate[]
