import unittest

import numpy as np

from dlgo.rl import experience


class ExperienceTest(unittest.TestCase):
    def test_combine_experience(self):
        collector1 = experience.ExperienceCollector()
        collector1.begin_episode()
        collector1.record_decision(
            state=np.array([
                [1, 1],
                [1, 1],
            ]),
            action=1,
        )
        collector1.record_decision(
            state=np.array([
                [2, 2],
                [2, 2],
            ]),
            action=2,
        )
        collector1.complete_episode(reward=1)

        collector1.begin_episode()
        collector1.record_decision(
            state=np.array([
                [3, 3],
                [3, 3],
            ]),
            action=3,
        )
        collector1.complete_episode(reward=2)

        collector2 = experience.ExperienceCollector()
        collector2.begin_episode()
        collector2.record_decision(
            state=np.array([
                [4, 4],
                [4, 4],
            ]),
            action=4,
        )
        collector2.complete_episode(reward=3)

        combined = experience.combine_experience([collector1, collector2])

        # 4 decisions. Each state is a 2x2 matrix
        self.assertEqual((4, 2, 2), combined.states.shape)
        self.assertEqual((4,), combined.actions.shape)
        self.assertEqual([1, 2, 3, 4], list(combined.actions))
        self.assertEqual((4,), combined.rewards.shape)
        self.assertEqual([1, 1, 2, 3], list(combined.rewards))
