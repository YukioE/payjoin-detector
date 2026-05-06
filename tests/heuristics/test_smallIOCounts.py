import unittest

from payjoin_detector.heuristics.smallIOCounts import SmallIOCountsHeuristic
from payjoin_detector.providers.esplora_provider import EsploraProvider
from tests import API

SMALL_IO_TX = "e788a31ef2f97e4d0a80ebb900834608fc99ce12d1dfb500a60ffc822ee1e546"
LARGE_IO_TX = "491937837833decfb14b106133fd53b34d87da217ff478eaecc96331f08f0cb3"


class TestSmallIOCountsHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = EsploraProvider(API)
        self.heuristic = SmallIOCountsHeuristic()
        self.small_io = await provider.get_transaction(SMALL_IO_TX)
        self.large_io = await provider.get_transaction(LARGE_IO_TX)

    def test_small_io_score(self):
        result = self.heuristic.check(self.small_io)
        self.assertGreater(result.score, 0.0)

    def test_small_io_counts_within_threshold(self):
        self.assertLessEqual(len(self.small_io.inputs), 5)
        self.assertLessEqual(len(self.small_io.outputs), 3)

    def test_large_io_score_is_neutral(self):
        result = self.heuristic.check(self.large_io)
        self.assertEqual(result.score, 0.0)

    def test_large_io_exceeds_threshold(self):
        exceeds = len(self.large_io.inputs) > 5 or len(self.large_io.outputs) > 3
        self.assertTrue(exceeds)


if __name__ == "__main__":
    unittest.main()
