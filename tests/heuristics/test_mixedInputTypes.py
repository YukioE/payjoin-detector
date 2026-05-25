import unittest

from payjoin_detector.heuristics.mixedInputTypes import MixedInputTypesHeuristic
from payjoin_detector.providers.electrs_provider import ElectrsProvider
from tests import API

MIXED_INPUTS_BEFORE_SEP2024_TX = (
    "e6ef5686bd6b30c21a6f9316dd170bdda049870caa91a367f228478c028954f3"
)
MIXED_INPUTS_AFTER_SEP2024_TX = (
    "6958d8c78c50f526fce234fafb34f4f5d7ca727676693fdd1ebdbe557736dab6"
)
UNIFORM_INPUTS_TX = "bd5534d47ed18456f2d4966408cf9009ade5733d5ee729732f4816bb96c61e85"


class TestMixedInputTypesHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = ElectrsProvider(API)
        self.heuristic = MixedInputTypesHeuristic()
        self.mixed_before = await provider.get_transaction(
            MIXED_INPUTS_BEFORE_SEP2024_TX
        )
        self.mixed_after = await provider.get_transaction(MIXED_INPUTS_AFTER_SEP2024_TX)
        self.uniform = await provider.get_transaction(UNIFORM_INPUTS_TX)

    def test_mixed_before_score_is_negative(self):
        result = self.heuristic.check(self.mixed_before)
        self.assertLess(result.score, 0.0)

    def test_mixed_after_score_is_neutral(self):
        result = self.heuristic.check(self.mixed_after)
        self.assertEqual(result.score, 0.0)

    def test_uniform_score_is_positive(self):
        result = self.heuristic.check(self.uniform)
        self.assertGreater(result.score, 0.0)


if __name__ == "__main__":
    unittest.main()
