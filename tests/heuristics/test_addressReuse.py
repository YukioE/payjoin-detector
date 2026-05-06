import unittest
from payjoin_detector.heuristics.addressReuse import AddressReuseHeuristic
from payjoin_detector.providers.esplora_provider import EsploraProvider
from tests import API

ADDRESS_REUSE_TX = "b92d778b8db32f0afc316e6b9885af97844efd547d7b049c6e9c9ffcaa87a70a"
NORMAL_TX = "f6146cbe2f7f18a62934eb338ac18762da35ad1b61aacb93eee13cb16761a1c7"


class TestAddressReuseHeuristic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        provider = EsploraProvider(API)
        self.heuristic = AddressReuseHeuristic()
        self.address_reuse_tx = await provider.get_transaction(ADDRESS_REUSE_TX)
        self.normal_tx = await provider.get_transaction(NORMAL_TX)

    def test_address_reuse_score_is_negative(self):
        result = self.heuristic.check(self.address_reuse_tx)
        self.assertLess(result.score, 0.0)

    def test_normal_tx_score_is_neutral(self):
        result = self.heuristic.check(self.normal_tx)
        self.assertEqual(result.score, 0.0)


if __name__ == "__main__":
    unittest.main()
