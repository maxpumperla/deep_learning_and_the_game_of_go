# Include the path to the local version of dlgo.
import os
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(dir_path, '..'))

# tag::e2e_imports[]
import h5py

from keras.models import Sequential
from keras.layers import Dense

from dlgo.agent.predict import DeepLearningAgent, load_prediction_agent
from dlgo.data.parallel_processor import GoDataProcessor
from dlgo.encoders.sevenplane import SevenPlaneEncoder
from dlgo.httpfrontend import get_web_app
from dlgo.networks import large
# end::e2e_imports[]

def main():
	# tag::e2e_processor[]
	go_board_rows, go_board_cols = 19, 19
	nb_classes = go_board_rows * go_board_cols
	encoder = SevenPlaneEncoder((go_board_rows, go_board_cols))
	processor = GoDataProcessor(encoder=encoder.name())

	X, y = processor.load_go_data(num_samples=100)
	# end::e2e_processor[]

	# tag::e2e_model[]
	input_shape = (encoder.num_planes, go_board_rows, go_board_cols)
	model = Sequential()
	network_layers = large.layers(input_shape)
	for layer in network_layers:
	    model.add(layer)
	model.add(Dense(nb_classes, activation='softmax'))
	model.compile(loss='categorical_crossentropy', optimizer='adadelta', metrics=['accuracy'])

	model.fit(X, y, batch_size=128, epochs=20, verbose=1)
	# end::e2e_model[]

	# tag::e2e_agent[]
	deep_learning_bot = DeepLearningAgent(model, encoder)
	model_file = h5py.File("../agents/deep_bot.h5", "w")
	deep_learning_bot.serialize(model_file)
	model_file.close()
	# end::e2e_agent[]

if __name__ == "__main__":
	main()
