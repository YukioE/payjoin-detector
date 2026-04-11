import unittest

from payjoin_detector.heuristics.coinJoin import CoinJoinHeuristic
from payjoin_detector.providers.esplora_provider import EsploraProvider

COINJOIN_TX = "ccaf0fa1999ebf474d14e97d725bf39d8a8db14832287751fcaa485b1f6399aa"
NORMAL_TX = "f6146cbe2f7f18a62934eb338ac18762da35ad1b61aacb93eee13cb16761a1c7"


class TestCoinJoinHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = EsploraProvider()
        self.heuristic = CoinJoinHeuristic()
        self.coinjoin_tx = await provider.get_transaction(COINJOIN_TX)
        self.normal_tx = await provider.get_transaction(NORMAL_TX)

    def test_coinjoin_score_is_negative(self):
        result = self.heuristic.check(self.coinjoin_tx)
        self.assertLess(result.score, 0.0)

    def test_normal_tx_score_is_neutral(self):
        result = self.heuristic.check(self.normal_tx)
        self.assertEqual(result.score, 0.0)


if __name__ == "__main__":
    unittest.main()
