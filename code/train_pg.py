import argparse

import h5py

from dlgo import agent
from dlgo import rl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--learning-agent', required=True)
    parser.add_argument('--agent-out', required=True)
    parser.add_argument('--lr', type=float, default=0.0001)
    parser.add_argument('--bs', type=int, default=512)
    parser.add_argument('experience', nargs='+')

    args = parser.parse_args()

    learning_agent = agent.load_policy_agent(h5py.File(args.learning_agent))
    for exp_filename in args.experience:
        print('Training with %s...' % exp_filename)
        exp_buffer = rl.load_experience(h5py.File(exp_filename))
        learning_agent.train(exp_buffer, lr=args.lr, batch_size=args.bs)

    with h5py.File(args.agent_out, 'w') as updated_agent_outf:
        learning_agent.serialize(updated_agent_outf)


if __name__ == '__main__':
    main()
