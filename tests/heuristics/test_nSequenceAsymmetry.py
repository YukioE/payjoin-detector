import unittest

from payjoin_detector.heuristics.nSequenceAsymmetry import NSequenceAsymmetryHeuristic
from payjoin_detector.providers.esplora_provider import EsploraProvider
from tests import API

ASYMMETRIC_SEQUENCE_TX = (
    "995d86343757ca77739daf770c1a704e701d776642a3b7f203d405825dcaf7a6"
)
UNIFORM_SEQUENCE_TX = "db3c9a3c812c48dd4011c9c941c1fdb5f0ba2a7cf0b6b7e897d12cf22704790f"


class TestNSequenceAsymmetryHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = EsploraProvider(API)
        self.heuristic = NSequenceAsymmetryHeuristic()
        self.asymmetric_tx = await provider.get_transaction(ASYMMETRIC_SEQUENCE_TX)
        self.uniform_tx = await provider.get_transaction(UNIFORM_SEQUENCE_TX)

    def test_asymmetric_score(self):
        result = self.heuristic.check(self.asymmetric_tx)
        self.assertGreater(result.score, 0.0)

    def test_uniform_score_is_neutral(self):
        result = self.heuristic.check(self.uniform_tx)
        self.assertEqual(result.score, 0.0)


if __name__ == "__main__":
    unittest.main()
