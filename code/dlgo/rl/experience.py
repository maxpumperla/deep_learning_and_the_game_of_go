import numpy as np

__all__ = [
    'ExperienceCollector',
    'ExperienceBuffer',
    'combine_experience',
    'load_experience',
]


class ExperienceCollector(object):
    def __init__(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self._current_episode_states = []
        self._current_episode_actions = []

    def begin_episode(self):
        self._current_episode_states = []
        self._current_episode_actions = []

    def record_decision(self, state, action):
        self._current_episode_states.append(state)
        self._current_episode_actions.append(action)

    def complete_episode(self, reward):
        num_states = len(self._current_episode_states)
        self.states += self._current_episode_states
        self.actions += self._current_episode_actions
        self.rewards += [reward for _ in range(num_states)]

        self._current_episode_states = []
        self._current_episode_actions = []


class ExperienceBuffer(object):
    def __init__(self, states, actions, rewards):
        self.states = states
        self.actions = actions
        self.rewards = rewards

    def serialize(self, h5file):
        h5file.create_group('experience')
        h5file['experience'].create_dataset('states', data=self.states)
        h5file['experience'].create_dataset('actions', data=self.actions)
        h5file['experience'].create_dataset('rewards', data=self.rewards)


def combine_experience(collectors):
    combined_states = np.concatenate([np.array(c.states) for c in collectors])
    combined_actions = np.concatenate([np.array(c.actions) for c in collectors])
    combined_rewards = np.concatenate([np.array(c.rewards) for c in collectors])

    return ExperienceBuffer(combined_states, combined_actions, combined_rewards)


def load_experience(h5file):
    return ExperienceBuffer(
        states=np.array(h5file['experience']['states']),
        actions=np.array(h5file['experience']['actions']),
        rewards=np.array(h5file['experience']['rewards']))
