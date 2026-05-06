import unittest

from payjoin_detector.providers.esplora_provider import EsploraProvider
from payjoin_detector.core.transaction import Transaction
from tests import API
from tests.providers.utils import (
    BLOCK_170_TX_1,
    BLOCK_170_TX_2,
    SIMPLE_BLOCK_HASH,
    SIMPLE_TX,
    TX_IDS,
    assert_inputs_equal,
    assert_outputs_equal,
    assert_tx_equal,
)


class TestGetTransaction(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.provider = EsploraProvider(API, use_async=True)

    async def test_returns_transaction(self):
        tx = await self.provider.get_transaction(SIMPLE_TX.txid)

        self.assertIsInstance(tx, Transaction)

        assert_tx_equal(self, tx, SIMPLE_TX)
        assert_inputs_equal(self, tx, SIMPLE_TX)
        assert_outputs_equal(self, tx, SIMPLE_TX)


class TestGetTransactions(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.provider = EsploraProvider(API, use_async=True)

    async def test_returns_transactions(self):
        txs = await self.provider.get_block_transactions(SIMPLE_BLOCK_HASH)

        self.assertIsInstance(txs, list)
        self.assertEqual(len(txs), 2)

        for tx in txs:
            self.assertIsInstance(tx, Transaction)

        assert_tx_equal(self, txs[0], BLOCK_170_TX_1)
        assert_tx_equal(self, txs[1], BLOCK_170_TX_2)

        assert_inputs_equal(self, txs[0], BLOCK_170_TX_1)
        assert_inputs_equal(self, txs[1], BLOCK_170_TX_2)

        assert_outputs_equal(self, txs[0], BLOCK_170_TX_1)
        assert_outputs_equal(self, txs[1], BLOCK_170_TX_2)


class TestFetchBlockTxIds(unittest.TestCase):
    def setUp(self):
        self.provider = EsploraProvider(API, use_async=True)

    def test_returns_txids(self):
        txid_list = self.provider._fetch_block_txids(SIMPLE_BLOCK_HASH)

        self.assertIsInstance(txid_list, list)
        self.assertEqual(txid_list, TX_IDS)
        self.assertTrue(all(isinstance(txid, str) for txid in txid_list))


if __name__ == "__main__":
    unittest.main()
