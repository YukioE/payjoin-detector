import unittest

from payjoin_detector.heuristics.roundFee import RoundFeeHeuristic
from payjoin_detector.providers.esplora_provider import EsploraProvider

ROUND_FEE_TX = "b369ca7dbf20ae4bc3e29d02c6adb322b1423dcdeac034c3539cc25a1fab6d22"
NON_ROUND_FEE_TX = "38081082052ae3a9887750c5b82a2c9e5e14460643cfe0e7b8f3ea7749d6a7d4"


class TestRoundFeeHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = EsploraProvider()
        self.round_fee_tx = await provider.get_transaction(ROUND_FEE_TX)
        self.non_round_fee_tx = await provider.get_transaction(NON_ROUND_FEE_TX)
        self.heuristic = RoundFeeHeuristic()

    def test_round_fee_tx_is_neutral(self):
        result = self.heuristic.check(self.round_fee_tx)
        self.assertEqual(result.score, 0.0)

    def test_non_round_fee_tx_is_negative(self):
        result = self.heuristic.check(self.non_round_fee_tx)
        self.assertLess(result.score, 0.0)
