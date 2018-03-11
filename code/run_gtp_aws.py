#!/usr/bin/python2
from dlgo.gtp import GTPFrontend
from dlgo.agent.predict import load_prediction_agent
from dlgo.agent import termination
import h5py

agent = load_prediction_agent(h5py.File("agents/betago.hdf5", "r"))
termination = termination.get("opponent_passes")

frontend = GTPFrontend(agent, termination)
frontend.run()
