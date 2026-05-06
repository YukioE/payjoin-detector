import unittest

from payjoin_detector.heuristics.signatureAsymmetry import SignatureAsymmetryHeuristic
from payjoin_detector.providers.esplora_provider import EsploraProvider
from tests import API

ASYMMETRIC_SIG_TX = "8fd0b699a36de72451f4bb42aa1b127af167f15afd1dcd42bb9f454d470533b3"
UNIFORM_SIG_TX = "cac7acd005a355684099ed650a16f1d7412e348c4b262cbd6538ddaae133d5d3"
MIXED_INPUT_TX = "db3568de377f4573b26679113ef2d40f7cd401c085880f823becca40ff822c1f"
NO_WITNESS_TX = "6762d24f8e7f9c2002f399cfea2b5423f196e6bc82924a32bc946422e387b0c5"


class TestSignatureAsymmetryHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = EsploraProvider(API)
        self.heuristic = SignatureAsymmetryHeuristic()
        self.asymmetric = await provider.get_transaction(ASYMMETRIC_SIG_TX)
        self.uniform = await provider.get_transaction(UNIFORM_SIG_TX)
        self.mixed_inputs = await provider.get_transaction(MIXED_INPUT_TX)
        self.no_witness = await provider.get_transaction(NO_WITNESS_TX)

    def test_asymmetric_score(self):
        result = self.heuristic.check(self.asymmetric)
        self.assertGreater(result.score, 0.0)

    def test_uniform_score_is_neutral(self):
        result = self.heuristic.check(self.uniform)
        self.assertEqual(result.score, 0.0)

    def test_mixed_input_types_score_is_neutral(self):
        result = self.heuristic.check(self.mixed_inputs)
        self.assertEqual(result.score, 0.0)

    def test_no_witness_score_is_neutral(self):
        result = self.heuristic.check(self.no_witness)
        self.assertEqual(result.score, 0.0)


if __name__ == "__main__":
    unittest.main()
