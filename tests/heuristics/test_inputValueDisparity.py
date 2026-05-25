import unittest

from payjoin_detector.heuristics.inputValueDisparity import InputValueDisparityHeuristic
from payjoin_detector.providers.electrs_provider import ElectrsProvider
from tests import API

HIGH_DISPARITY_TX = "5cf5f319a4808b33eae9f0d802ec82980f0fc638118119d8edba9ab54408923e"
LOW_DISPARITY_TX = "6f7db00999e3de851a0de7fa9d565bf573d8a3d1bcb023a2697cdfe28d5d40dc"


class TestInputValueDisparityHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = ElectrsProvider(API)
        self.heuristic = InputValueDisparityHeuristic()
        self.high_disparity_tx = await provider.get_transaction(HIGH_DISPARITY_TX)
        self.low_disparity_tx = await provider.get_transaction(LOW_DISPARITY_TX)

    def test_high_disparity_score(self):
        result = self.heuristic.check(self.high_disparity_tx)
        self.assertGreater(result.score, 0.0)

    def test_low_disparity_score_is_neutral(self):
        result = self.heuristic.check(self.low_disparity_tx)
        self.assertEqual(result.score, 0.0)


if __name__ == "__main__":
    unittest.main()
