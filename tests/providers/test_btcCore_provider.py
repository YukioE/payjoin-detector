import unittest
import os

from payjoin_detector.providers.btcCore_provider import BitcoinCoreProvider
from payjoin_detector.core.transaction import Transaction
from tests.providers.utils import (
    BLOCK_170_TX_1,
    BLOCK_170_TX_2,
    SIMPLE_BLOCK_HASH,
    SIMPLE_TX,
    assert_tx_equal,
    assert_inputs_equal,
    assert_outputs_equal,
)


class TestGetTransaction(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.provider = BitcoinCoreProvider(
            os.environ["BITCOIN_RPC_URL"],
            os.environ["BITCOIN_RPC_USER"],
            os.environ["BITCOIN_RPC_PASS"],
            use_async=True,
        )

    async def test_returns_transaction(self):
        tx = await self.provider.get_transaction(SIMPLE_TX.txid)
        self.assertIsInstance(tx, Transaction)

        assert_tx_equal(self, tx, SIMPLE_TX)
        assert_inputs_equal(self, tx, SIMPLE_TX)
        assert_outputs_equal(self, tx, SIMPLE_TX)


class TestGetTransactions(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.provider = BitcoinCoreProvider(
            os.environ["BITCOIN_RPC_URL"],
            os.environ["BITCOIN_RPC_USER"],
            os.environ["BITCOIN_RPC_PASS"],
            use_async=True,
        )

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


if __name__ == "__main__":
    unittest.main()
