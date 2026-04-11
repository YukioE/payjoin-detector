import unittest

from payjoin_detector.heuristics.roundPaymentAssignment import (
    RoundPaymentAssignmentHeuristic,
)
from payjoin_detector.providers.esplora_provider import EsploraProvider

ROUND_PAYMENT_TX = "ca243920046b3ac028fbb4ba9e25ee3c675040e93d13180d6608a1e0e7fcc43b"
NO_ROUND_PAYMENT_TX = "8fd0b699a36de72451f4bb42aa1b127af167f15afd1dcd42bb9f454d470533b3"


class TestRoundPaymentAssignmentHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = EsploraProvider()
        self.heuristic = RoundPaymentAssignmentHeuristic()
        self.round_tx = await provider.get_transaction(ROUND_PAYMENT_TX)
        self.no_round_tx = await provider.get_transaction(NO_ROUND_PAYMENT_TX)

    def test_round_payment_score(self):
        result = self.heuristic.check(self.round_tx)
        self.assertGreater(result.score, 0.0)

    def test_no_round_payment_score_is_neutral(self):
        result = self.heuristic.check(self.no_round_tx)
        self.assertEqual(result.score, 0.0)


if __name__ == "__main__":
    unittest.main()
