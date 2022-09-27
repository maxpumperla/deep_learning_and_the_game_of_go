from __future__ import print_function
# tag::imports[]
import numpy as np
# end::imports[]


# tag::sigmoid[]
def sigmoid_double(x):
    return 1.0 / (1.0 + np.exp(-x))


def sigmoid(z):
    return np.reciprocal(np.add(1.0, np.exp(-z)))
# end::sigmoid[]


# tag::sigmoid_prime[]
def sigmoid_prime_double(x):
    return sigmoid_double(x) * (1 - sigmoid_double(x))


def sigmoid_prime(z):
    return np.multiply(sigmoid(z),np.subtract(1,sigmoid(z)))
# end::sigmoid_prime[]


# tag::layer[]
class Layer(object):  # <1>
    def __init__(self):
        self.params = []

        self.previous = None  # <2>
        self.next = None  # <3>

        self.input_data = None  # <4>
        self.output_data = None

        self.input_delta = None  # <5>
        self.output_delta = None
# <1> Layers are stacked to build a sequential neural network.
# <2> A layer knows its predecessor ('previous')...
# <3> ... and its successor ('next').
# <4> Each layer can persist data flowing into and out of it in the forward pass.
# <5> Analogously, a layer holds input and output data for the backward pass.
# end::layer[]

# tag::connect[]
    def connect(self, layer):  # <1>
        self.previous = layer
        layer.next = self
# <1>  This method connects a layer to its direct neighbours in the sequential network.
# end::connect[]

# tag::forward_backward[]
    def forward(self):  # <1>
        raise NotImplementedError

    def get_forward_input(self):  # <2>
        if self.previous is not None:
            return self.previous.output_data
        else:
            return self.input_data

    def backward(self):  # <3>
        raise NotImplementedError

    def get_backward_input(self):  # <4>
        if self.next is not None:
            return self.next.output_delta
        else:
            return self.input_delta

    def clear_deltas(self):  # <5>
        pass

    def update_params(self, learning_rate):  # <6>
        pass

    def describe(self):  # <7>
        raise NotImplementedError

# <1> Each layer implementation has to provid a function to feed input data forward.
# <2> input_data is reserved for the first layer, all others get their input from the previous output.
# <3> Layers have to implement backpropagation of error terms, that is a way to feed input errors backward through the network.
# <4> Input delta is reserved for the last layer, all other layers get their error terms from their successor.
# <5> We compute and accumulate deltas per mini-batch, after which we need to reset these deltas.
# <6> Update layer parameters according to current deltas, using the specified learning_rate.
# <7> Layer implementations can print their properties.
# end::forward_backward[]


# tag::activation_layer[]
class ActivationLayer(Layer):  # <1>
    def __init__(self, input_dim):
        super(ActivationLayer, self).__init__()

        self.input_dim = input_dim
        self.output_dim = input_dim

    def forward(self):
        data = self.get_forward_input()
        self.output_data = sigmoid(data)  # <2>

    def backward(self):
        delta = self.get_backward_input()
        data = self.get_forward_input()
        self.output_delta = delta * sigmoid_prime(data)  # <3>

    def describe(self):
        print("|-- " + self.__class__.__name__)
        print("  |-- dimensions: ({},{})"
              .format(self.input_dim, self.output_dim))
# <1> This activation layer uses the sigmoid function to activate neurons.
# <2> The forward pass is simply applying the sigmoid to the input data.
# <3> The backward pass is element-wise multiplication of the error term with the sigmoid derivative evaluated at the input to this layer.
# end::activation_layer[]


# tag::dense_init[]
class DenseLayer(Layer):

    def __init__(self, input_dim, output_dim):  # <1>

        super(DenseLayer, self).__init__()

        self.input_dim = input_dim
        self.output_dim = output_dim

        self.weight = np.random.randn(output_dim, input_dim)  # <2>
        self.bias = np.random.randn(output_dim, 1)

        self.params = [self.weight, self.bias]  # <3>

        self.delta_w = np.zeros(self.weight.shape)  # <4>
        self.delta_b = np.zeros(self.bias.shape)

# <1> Dense layers have input and output dimensions.
# <2> We randomly initialize weight matrix and bias vector.
# <3> The layer parameters consist of weights and bias terms.
# <4> Deltas for weights and biases are set to zero.
# end::dense_init[]

# tag::dense_forward[]
    def forward(self):
        data = self.get_forward_input()
        self.output_data = np.dot(self.weight, data) + self.bias  # <1>

# <1> The forward pass of the dense layer is the affine linear transformation on input data defined by weights and biases.
# end::dense_forward[]

# tag::dense_backward[]
    def backward(self):
        data = self.get_forward_input()
        delta = self.get_backward_input()  # <1>

        self.delta_b += delta  # <2>

        self.delta_w += np.dot(delta, data.transpose())  # <3>

        self.output_delta = np.dot(self.weight.transpose(), delta)  # <4>

# <1> For the backward pass we first get input data and delta.
# <2> The current delta is added to the bias delta.
# <3> Then we add this term to the weight delta.
# <4> The backward pass is completed by passing an output delta to the previous layer.
# end::dense_backward[]

# tag::dense_update[]
    def update_params(self, rate):  # <1>
        self.weight -= rate * self.delta_w
        self.bias -= rate * self.delta_b

    def clear_deltas(self):  # <2>
        self.delta_w = np.zeros(self.weight.shape)
        self.delta_b = np.zeros(self.bias.shape)

    def describe(self):  # <3>
        print("|--- " + self.__class__.__name__)
        print("  |-- dimensions: ({},{})"
              .format(self.input_dim, self.output_dim))
# <1> Using weight and bias deltas we can update model parameters with gradient descent.
# <2> After updating parameters we should reset all deltas.
# <3> A dense layer can be described by its input and output dimensions.
# end::dense_update[]
