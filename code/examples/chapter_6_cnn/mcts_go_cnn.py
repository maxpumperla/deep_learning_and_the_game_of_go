from __future__ import print_function

# tag::mcts_go_cnn_preprocessing[]
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D

np.random.seed(123)
X = np.load('../generated_games/features-40k.npy')
Y = np.load('../generated_games/labels-40k.npy')

samples = X.shape[0]
size = 9
input_shape = (size, size, 1)

X = X.reshape(samples, size, size, 1)

train_samples = int(0.9 * samples)
X_train, X_test = X[:train_samples], X[train_samples:]
Y_train, Y_test = Y[:train_samples], Y[train_samples:]
# end::mcts_go_cnn_preprocessing[]

# tag::mcts_go_cnn_model[]
model = Sequential()
model.add(Conv2D(48, kernel_size=(3, 3),
                 activation='relu',
                 padding='same',
                 input_shape=input_shape))
model.add(Dropout(rate=0.5))
model.add(Conv2D(48, (3, 3),
                 padding='same', activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(rate=0.5))
model.add(Flatten())
model.add(Dense(512, activation='relu'))
model.add(Dropout(rate=0.5))
model.add(Dense(size * size, activation='softmax'))
model.summary()

model.compile(loss='categorical_crossentropy',
              optimizer='sgd',
              metrics=['accuracy'])
# end::mcts_go_cnn_model[]

# tag::mcts_go_cnn_eval[]
model.fit(X_train, Y_train,
          batch_size=64,
          epochs=100,
          verbose=1,
          validation_data=(X_test, Y_test))
score = model.evaluate(X_test, Y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
# end::mcts_go_cnn_eval[]

test_board = np.array([[[
    0, 0,  0,  0,  0, 0, 0, 0, 0,
    0, 0,  0,  0,  0, 0, 0, 0, 0,
    0, 0,  0,  0,  0, 0, 0, 0, 0,
    0, 1, -1,  1, -1, 0, 0, 0, 0,
    0, 1, -1,  1, -1, 0, 0, 0, 0,
    0, 0,  1, -1,  0, 0, 0, 0, 0,
    0, 0,  0,  0,  0, 0, 0, 0, 0,
    0, 0,  0,  0,  0, 0, 0, 0, 0,
    0, 0,  0,  0,  0, 0, 0, 0, 0,
]]]).reshape(1, 9, 9, 1)
move_probs = model.predict(test_board)[0]
i = 0
for row in range(9):
    row_formatted = []
    for col in range(9):
        row_formatted.append('{:.3f}'.format(move_probs[i]))
        i += 1
    print(' '.join(row_formatted))
