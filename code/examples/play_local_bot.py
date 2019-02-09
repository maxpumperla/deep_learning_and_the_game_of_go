# tag::gtp_pachi[]
from dlgo.gtp.play_local import LocalGtpBot
from dlgo.agent.termination import PassWhenOpponentPasses
from dlgo.agent.predict import load_prediction_agent
import h5py

import os
adirCode=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

afileBetago=os.path.join(adirCode,"agents/betago.hdf5")
bot = load_prediction_agent(h5py.File(afileBetago, "r"))

gtp_bot = LocalGtpBot(go_bot=bot, termination=PassWhenOpponentPasses(),
                      handicap=0, opponent='pachi')
gtp_bot.run()
# end::gtp_pachi[]
