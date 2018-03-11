# tag::avg_imports[]
import numpy as np
from dlgo.nn.load_mnist import load_data
from dlgo.nn.layers import sigmoid_double
# end::avg_imports[]


# tag::average_digit[]
def average_digit(data, digit):  # <1>
    filtered_data = [x[0] for x in data if np.argmax(x[1]) == digit]
    filtered_array = np.asarray(filtered_data)
    return np.average(filtered_array, axis=0)


train, test = load_data()
avg_eight = average_digit(train, 8)  # <2>

# <1> We compute the average over all samples in our data representing a given digit.
# <2> We use the average eight as parameters for a simple model to detect eights.
# end::average_digit[]

# tag::display_digit[]
from matplotlib import pyplot as plt

img = (np.reshape(avg_eight, (28, 28)))
plt.imshow(img)
plt.show()
# end::display_digit[]

# tag::eval_eight[]
x_3 = train[2][0]    # <1>
x_18 = train[17][0]  # <2>

W = np.transpose(avg_eight)
np.dot(W, x_3)   # <3>
np.dot(W, x_18)  # <4>

# <1> Training sample at index 2 is a "4".
# <2> Training sample at index 17 is an "8"
# <3> This evaluates to about 20.1.
# <4> This term is much bigger, about 54.2.
# end::eval_eight[]


# tag::predict_simple[]
def predict(x, W, b):  # <1>
    return sigmoid_double(np.dot(W, x) + b)


b = -45  # <2>

print(predict(x_3, W, b))   # <3>
print(predict(x_18, W, b))  # <4> 0.96

# <1> A simple prediction is defined by applying sigmoid to the output of np.doc(W, x) + b.
# <2> Based on the examples computed so far we set the bias term to -45.
# <3> The prediction for the example with a "4" is close to zero.
# <5> The prediction for an "8" is 0.96 here. We seem to be onto something with our heuristic.
# end::predict_simple[]


# tag::evaluate_simple[]
def evaluate(data, digit, threshold, W, b):  # <1>
    total_samples = 1.0 * len(data)
    correct_predictions = 0
    for x in data:
        if predict(x[0], W, b) > threshold and np.argmax(x[1]) == digit:  # <2>
            correct_predictions += 1
        if predict(x[0], W, b) <= threshold and np.argmax(x[1]) != digit:  # <3>
            correct_predictions += 1
    return correct_predictions / total_samples

# <1> As evaluation metric we choose accuracy, the ratio of correct predictions among all.
# <2> Predicting an instance of an eight as "8" is a correct prediction.
# <3> If the prediction is below our threshold and the sample is not an "8", we also predicted correctly.
# end::evaluate_simple[]


# tag::evaluate_example[]
evaluate(data=train, digit=8, threshold=0.5, W=W, b=b)  # <1>

evaluate(data=test, digit=8, threshold=0.5, W=W, b=b)   # <2>

eight_test = [x for x in test if np.argmax(x[1]) == 8]
evaluate(data=eight_test, digit=8, threshold=0.5, W=W, b=b)  # <3>

# <1> Accuracy on training data of our simple model is 78% (0.7814)
# <2> Accuracy on test data is slightly lower, at 77% (0.7749)
# <3> Evaluating only on the set of eights in the test set only results in 67% accuracy (0.6663)
# end::evaluate_example[]
