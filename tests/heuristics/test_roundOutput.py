import unittest

from payjoin_detector.heuristics.roundOutput import RoundOutputHeuristic
from payjoin_detector.providers.electrs_provider import ElectrsProvider
from tests import API

ALL_ROUND_OUTPUTS_TX = (
    "ca243920046b3ac028fbb4ba9e25ee3c675040e93d13180d6608a1e0e7fcc43b"
)
ALL_NONROUND_OUTPUTS_TX = (
    "995d86343757ca77739daf770c1a704e701d776642a3b7f203d405825dcaf7a6"
)
MIXED_OUTPUTS_TX = "721c167b4524d5b2860013bb44388a4224c43eec9c03bc712f78834193ca7987"


class TestRoundOutputHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = ElectrsProvider(API)
        self.heuristic = RoundOutputHeuristic()
        self.all_round_tx = await provider.get_transaction(ALL_ROUND_OUTPUTS_TX)
        self.all_nonround_tx = await provider.get_transaction(ALL_NONROUND_OUTPUTS_TX)
        self.mixed_tx = await provider.get_transaction(MIXED_OUTPUTS_TX)

    def test_all_round_score_is_negative(self):
        result = self.heuristic.check(self.all_round_tx)
        self.assertLess(result.score, 0.0)

    def test_all_nonround_score_is_positive(self):
        result = self.heuristic.check(self.all_nonround_tx)
        self.assertGreater(result.score, 0.0)

    def test_mixed_score_is_slightly_negative(self):
        result = self.heuristic.check(self.mixed_tx)
        self.assertLess(result.score, 0.0)


if __name__ == "__main__":
    unittest.main()
