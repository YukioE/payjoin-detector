import unittest

from payjoin_detector.heuristics.mixedOutputTypes import MixedOutputTypesHeuristic
from payjoin_detector.providers.electrs_provider import ElectrsProvider
from tests import API

MIXED_OUTPUTS_TX = "db3c9a3c812c48dd4011c9c941c1fdb5f0ba2a7cf0b6b7e897d12cf22704790f"
UNIFORM_OUTPUTS_TX = "8026864b4eda41e32135e03dd3ba404ecf6b58decdd5867d011a3804db977005"


class TestMixedOutputTypesHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = ElectrsProvider(API)
        self.heuristic = MixedOutputTypesHeuristic()
        self.mixed_tx = await provider.get_transaction(MIXED_OUTPUTS_TX)
        self.uniform_tx = await provider.get_transaction(UNIFORM_OUTPUTS_TX)

    def test_mixed_outputs_score_is_neutral(self):
        result = self.heuristic.check(self.mixed_tx)
        self.assertEqual(result.score, 0.0)

    def test_uniform_outputs_score_is_positive(self):
        result = self.heuristic.check(self.uniform_tx)
        self.assertGreater(result.score, 0.0)


if __name__ == "__main__":
    unittest.main()
