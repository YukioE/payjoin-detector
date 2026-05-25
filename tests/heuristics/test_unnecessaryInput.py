import unittest

from payjoin_detector.heuristics.unnecessaryInput import UnnecessaryInputHeuristic
from payjoin_detector.providers.electrs_provider import ElectrsProvider
from tests import API

UIH2_TX = "c09d242893a59e606ee70615f7619f687e6a9f506004db1dfe4a06aef4b16d53"
UIH1_TX = "7120d9408a71a03c219c1cfd677a59febea61af3aa585b0022fe2d5094a87a26"


class TestUnnecessaryInputHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = ElectrsProvider(API)
        self.heuristic = UnnecessaryInputHeuristic()
        self.uih2_tx = await provider.get_transaction(UIH2_TX)
        self.uih1_tx = await provider.get_transaction(UIH1_TX)

    def test_uih2_score(self):
        result = self.heuristic.check(self.uih2_tx)
        self.assertGreater(result.score, 0.0)

    def test_uih2_condition_holds_on_tx(self):
        input_values = [i.prevout.value for i in self.uih2_tx.inputs if i.prevout]
        output_values = [o.value for o in self.uih2_tx.outputs]
        self.assertGreater(min(output_values), min(input_values))

    def test_uih1_score_is_neutral(self):
        result = self.heuristic.check(self.uih1_tx)
        self.assertEqual(result.score, 0.0)

    def test_uih1_condition_holds_on_tx(self):
        input_values = [i.prevout.value for i in self.uih1_tx.inputs if i.prevout]
        output_values = [o.value for o in self.uih1_tx.outputs]
        self.assertLessEqual(min(output_values), min(input_values))


if __name__ == "__main__":
    unittest.main()
