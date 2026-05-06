import unittest

from payjoin_detector.heuristics.clustering import ClusteringHeuristic
from payjoin_detector.providers.esplora_provider import EsploraProvider
from tests import API

SINGLE_CLUSTER_TX = "78c6b27fee85f315fc7efea439e734af134136b96f5a9cfa6dcf4f4a6c88aa4f"
MULTIPLE_CLUSTER_TX = "e15c78ce01caeb85ba035f65b2afbe7e8b9d035bfe999b765b68df191aa4847c"


class TestClusteringHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = EsploraProvider(API, use_async=True)
        self.single_cluster_tx = await provider.get_transaction(SINGLE_CLUSTER_TX)
        self.multiple_cluster_tx = await provider.get_transaction(MULTIPLE_CLUSTER_TX)

        self.single_cluster_tx_history = await provider.get_cluster_transactions(
            self.single_cluster_tx, 1, 10
        )
        self.multiple_cluster_tx_history = await provider.get_cluster_transactions(
            self.multiple_cluster_tx, 1, 10
        )

    def test_single_cluster_is_negative(self):
        self.heuristic = ClusteringHeuristic(self.single_cluster_tx_history)
        result = self.heuristic.check(self.single_cluster_tx)
        self.assertLess(result.score, 0.0)

    def test_multiple_cluster_is_neutral(self):
        self.heuristic = ClusteringHeuristic(self.multiple_cluster_tx_history)
        result = self.heuristic.check(self.multiple_cluster_tx)
        self.assertEqual(result.score, 0.0)


if __name__ == "__main__":
    unittest.main()
