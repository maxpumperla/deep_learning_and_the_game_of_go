import argparse

import h5py

# from dlgo import agent
from dlgo import elo
from dlgo import rl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-games', '-g', type=int)
    parser.add_argument('--board-size', '-b', type=int)
    parser.add_argument('agents', nargs='+')

    args = parser.parse_args()

    agents = [
        # agent.load_policy_agent(h5py.File(filename))
        rl.load_q_agent(h5py.File(filename))
        for filename in args.agents]
    for a in agents:
        a.set_temperature(0.02)

    ratings = elo.calculate_ratings(agents, args.num_games, args.board_size)

    for filename, rating in zip(args.agents, ratings):
        print("%s %d" % (filename, rating))


if __name__ == '__main__':
    main()
