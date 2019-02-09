#!/usr/local/bin/python2
from dlgo.gtp import GTPFrontend
from dlgo.agent.predict import load_prediction_agent
from dlgo.agent import termination
import h5py

import os
adirCode=os.path.dirname(os.path.abspath(__file__))

afileBetago=os.path.join(adirCode,"agents/betago.hdf5")
model_file = h5py.File(afileBetago, "r")
agent = load_prediction_agent(model_file)
strategy = termination.get("opponent_passes")
termination_agent = termination.TerminationAgent(agent, strategy)

frontend = GTPFrontend(termination_agent)
frontend.run()
