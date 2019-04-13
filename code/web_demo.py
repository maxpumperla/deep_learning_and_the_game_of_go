import argparse

import h5py

from dlgo import agent
from dlgo import httpfrontend
from dlgo import mcts
from dlgo import rl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind-address', default='127.0.0.1')
    parser.add_argument('--port', '-p', type=int, default=5000)
    parser.add_argument('--pg-agent')
    parser.add_argument('--predict-agent')
    parser.add_argument('--q-agent')
    parser.add_argument('--ac-agent')

    args = parser.parse_args()

    bots = {'mcts': mcts.MCTSAgent(800, temperature=0.7)}
    if args.pg_agent:
        bots['pg'] = agent.load_policy_agent(h5py.File(args.pg_agent))
    if args.predict_agent:
        bots['predict'] = agent.load_prediction_agent(
            h5py.File(args.predict_agent))
    if args.q_agent:
        q_bot = rl.load_q_agent(h5py.File(args.q_agent))
        q_bot.set_temperature(0.01)
        bots['q'] = q_bot
    if args.ac_agent:
        ac_bot = rl.load_ac_agent(h5py.File(args.ac_agent))
        ac_bot.set_temperature(0.05)
        bots['ac'] = ac_bot

    web_app = httpfrontend.get_web_app(bots)
    web_app.run(host=args.bind_address, port=args.port, threaded=False)


if __name__ == '__main__':
    main()
