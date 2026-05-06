import unittest

from payjoin_detector.api import analyse_txid, analyse_block
from payjoin_detector.core.provider import TransactionNotFoundError, ProviderError
from payjoin_detector.providers.esplora_provider import EsploraProvider
from tests import API

COINBASE_TX = "b3d07da948174762f25cc28d9a5452350724af0e7fa96e84b735660305aac989"
POTENTIAL_PAYJOIN_TX = (
    "f6146cbe2f7f18a62934eb338ac18762da35ad1b61aacb93eee13cb16761a1c7"
)
ONE_INPUT_TX = "eb07176fb0d82a1b1bc37409b454fdf19b75c20be1a005085f3c631680e30ed3"
BLOCK_HASH = "00000000d1145790a8694403d4063f323d499e655c83426834d4ce2f8dd4a2ee"


class TestAnalyseTxid(unittest.IsolatedAsyncioTestCase):
    async def test_returns_float(self):
        result = await analyse_txid(POTENTIAL_PAYJOIN_TX, EsploraProvider(API))
        self.assertIsInstance(result, float)

    async def test_confidence_clamped_between_0_and_1(self):
        result = await analyse_txid(POTENTIAL_PAYJOIN_TX, EsploraProvider(API))
        self.assertGreater(result, 0.0)
        self.assertLess(result, 1.0)

    async def test_coinbase_returns_zero_confidence(self):
        result = await analyse_txid(COINBASE_TX, EsploraProvider(API))
        self.assertEqual(result, 0.0)

    async def test_single_input_returns_zero_confidence(self):
        result = await analyse_txid(ONE_INPUT_TX, EsploraProvider(API))
        self.assertEqual(result, 0.0)

    async def test_raises_transaction_not_found(self):
        with self.assertRaises(TransactionNotFoundError):
            await analyse_txid(
                "0000000000000000000000000000000000000000000000000000000000000000",
                EsploraProvider(API),
            )

    async def test_raises_provider_error_on_bad_base_url(self):
        provider = EsploraProvider(base_url="https://invalid.invalid/api")
        with self.assertRaises(ProviderError):
            await analyse_txid(POTENTIAL_PAYJOIN_TX, provider=provider)


class TestAnalyseBlock(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.result = await analyse_block(BLOCK_HASH, EsploraProvider(API))

    async def test_returns_dict(self):
        self.assertIsInstance(self.result, dict)

    async def test_keys_are_txid_strings(self):
        for key in self.result:
            self.assertIsInstance(key, str)
            self.assertEqual(len(key), 2)

    async def test_values_are_floats(self):
        for value in self.result.values():
            self.assertIsInstance(value, float)

    async def test_all_values_clamped_between_0_and_1(self):
        for value in self.result.values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    async def test_default_threshold_filters_low_confidence(self):
        for value in self.result.values():
            self.assertGreaterEqual(value, 0.1)

    async def test_zero_threshold_returns_all_txs(self):
        result = await analyse_block(BLOCK_HASH, EsploraProvider(API), threshold=0.0)
        self.assertEqual(len(result), 2)

    async def test_raises_block_not_found(self):
        from payjoin_detector.core.provider import BlockNotFoundError

        with self.assertRaises(BlockNotFoundError):
            await analyse_block(
                "0000000000000000000000000000000000000000000000000000000000000000",
                EsploraProvider(API),
            )

    async def test_raises_provider_error_on_bad_base_url(self):
        provider = EsploraProvider(base_url="https://invalid.invalid/api")
        with self.assertRaises(ProviderError):
            await analyse_block(BLOCK_HASH, provider=provider)


if __name__ == "__main__":
    unittest.main()
