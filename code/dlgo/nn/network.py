from __future__ import print_function
from six.moves import range
# tag::mse[]
import random
import numpy as np


class MSE:  # <1>

    def __init__(self):
        pass

    @staticmethod
    def loss_function(predictions, labels):
        diff = predictions - labels
        return 0.5 * sum(diff * diff)[0]  # <2>

    @staticmethod
    def loss_derivative(predictions, labels):
        return predictions - labels

# <1> We use mean squared error as our loss function.
# <2> By defining MSE as 0.5 times the square difference between predictions and labels...
# <3> ... the loss derivative is simply: predictions - labels.
# end::mse[]


# tag::sequential_init[]
class SequentialNetwork:  # <1>
    def __init__(self, loss=None):
        print("Initialize Network...")
        self.layers = []
        if loss is None:
            self.loss = MSE()  # <2>

# <1> In a sequential neural network we stack layers sequentially.
# <2> If no loss function is provided, MSE is used.
# end::sequential_init[]

# tag::add_layers[]
    def add(self, layer):  # <1>
        self.layers.append(layer)
        layer.describe()
        if len(self.layers) > 1:
            self.layers[-1].connect(self.layers[-2])

# <1> Whenever we add a layer, we connect it to its predecessor and let it describe itself.
# end::add_layers[]

# tag::train[]
    def train(self, training_data, epochs, mini_batch_size,
              learning_rate, test_data=None):
        n = len(training_data)
        for epoch in range(epochs):  # <1>
            random.shuffle(training_data)
            mini_batches = [
                training_data[k:k + mini_batch_size] for
                k in range(0, n, mini_batch_size)  # <2>
            ]
            for mini_batch in mini_batches:
                self.train_batch(mini_batch, learning_rate)  # <3>
            if test_data:
                n_test = len(test_data)
                print("Epoch {0}: {1} / {2}"
                      .format(epoch, self.evaluate(test_data), n_test))  # <4>
            else:
                print("Epoch {0} complete".format(epoch))

# <1> To train our network, we pass over data for as many times as there are epochs.
# <2> We shuffle training data and create mini-batches.
# <3> For each mini-batch we train our network.
# <4> In case we provided test data, we evaluate our network on it after each epoch.
# end::train[]

# tag::train_batch[]
    def train_batch(self, mini_batch, learning_rate):
        self.forward_backward(mini_batch)  # <1>

        self.update(mini_batch, learning_rate)  # <2>

# <1> To train the network on a mini-batch, we compute feed-forward and backward pass...
# <2> ... and then update model parameters accordingly.
# end::train_batch[]

# tag::update_ff_bp[]
    def update(self, mini_batch, learning_rate):
        learning_rate = learning_rate / len(mini_batch)  # <1>
        for layer in self.layers:
            layer.update_params(learning_rate)  # <2>
        for layer in self.layers:
            layer.clear_deltas()  # <3>

    def forward_backward(self, mini_batch):
        for x, y in mini_batch:
            self.layers[0].input_data = x
            for layer in self.layers:
                layer.forward()  # <4>
            self.layers[-1].input_delta = \
                self.loss.loss_derivative(self.layers[-1].output_data, y)  # <5>
            for layer in reversed(self.layers):
                layer.backward()  # <6>

# <1> A common technique is to normalize the learning rate by the mini-batch size.
# <2> We then update parameters for all layers.
# <3> Afterwards we clear all deltas in each layer.
# <4> For each sample in the mini batch, feed the features forward layer by layer.
# <5> Next, we compute the loss derivative for the output data.
# <6> Finally, we do layer-by-layer backpropagation of error terms.
# end::update_ff_bp[]

# tag::eval[]
    def single_forward(self, x):  # <1>
        self.layers[0].input_data = x
        for layer in self.layers:
                layer.forward()
        return self.layers[-1].output_data

    def evaluate(self, test_data):  # <2>
        test_results = [(
            np.argmax(self.single_forward(x)),
            np.argmax(y)
        ) for (x, y) in test_data]
        return sum(int(x == y) for (x, y) in test_results)
# <1> Pass a single sample forward and return the result.
# <2> Compute accuracy on test data.
# end::eval[]
