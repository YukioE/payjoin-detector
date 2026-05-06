import unittest

from payjoin_detector.detector import Detector
from payjoin_detector.core.detection import BlockDetectionResult, TxDetectionResult
from payjoin_detector.core.provider import TransactionNotFoundError, ProviderError
from payjoin_detector.providers.esplora_provider import EsploraProvider
from tests import API

COINBASE_TX = "b3d07da948174762f25cc28d9a5452350724af0e7fa96e84b735660305aac989"
POTENTIAL_PAYJOIN_TX = (
    "f6146cbe2f7f18a62934eb338ac18762da35ad1b61aacb93eee13cb16761a1c7"
)
ONE_INPUT_TX = "eb07176fb0d82a1b1bc37409b454fdf19b75c20be1a005085f3c631680e30ed3"
ONE_OUTPUT_TX = "8a416edc5d111b5fadbe9dac468d21f55623c9b4a261bfacac4f86a95bb65cb2"
BLOCK_HASH = "00000000d1145790a8694403d4063f323d499e655c83426834d4ce2f8dd4a2ee"


class TestCheckPayjoinPossible(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.provider = EsploraProvider(API, use_async=True)
        self.detector = Detector(self.provider)

    async def test_valid_tx_returns_true(self):
        tx = await self.provider.get_transaction(POTENTIAL_PAYJOIN_TX)
        self.assertTrue(self.detector.check_payjoin_possible(tx))

    async def test_coinbase_returns_false(self):
        tx = await self.provider.get_transaction(COINBASE_TX)
        self.assertFalse(self.detector.check_payjoin_possible(tx))

    async def test_single_input_address_returns_false(self):
        tx = await self.provider.get_transaction(ONE_INPUT_TX)
        self.assertFalse(self.detector.check_payjoin_possible(tx))

    async def test_single_output_address_returns_false(self):
        tx = await self.provider.get_transaction(ONE_OUTPUT_TX)
        self.assertFalse(self.detector.check_payjoin_possible(tx))


class TestAnalyse(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.provider = EsploraProvider(API, use_async=True)
        self.detector = Detector(self.provider)
        self.tx = await self.provider.get_transaction(POTENTIAL_PAYJOIN_TX)
        self.result = self.detector.analyse(self.tx)

    async def test_returns_tx_detection_result(self):
        self.assertIsInstance(self.result, TxDetectionResult)

    async def test_result_txid_preserved(self):
        self.assertEqual(self.result.txid, POTENTIAL_PAYJOIN_TX)

    async def test_result_io_counts(self):
        self.assertEqual(self.result.input_count, 2)
        self.assertEqual(self.result.output_count, 2)

    async def test_confidence_clamped_between_0_and_1(self):
        self.assertGreater(self.result.confidence, 0.0)
        self.assertLess(self.result.confidence, 1.0)

    async def test_payjoin_not_possible_returns_zero_confidence(self):
        tx = await self.provider.get_transaction(COINBASE_TX)
        result = self.detector.analyse(tx)
        self.assertEqual(result.confidence, 0.0)


class TestDetect(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.provider = EsploraProvider(API, use_async=True)
        self.detector = Detector(self.provider)
        self.tx = await self.provider.get_transaction(POTENTIAL_PAYJOIN_TX)

    async def test_returns_tx_detection_result(self):
        result = await self.detector.detect(POTENTIAL_PAYJOIN_TX)
        self.assertIsInstance(result, TxDetectionResult)

    async def test_propagates_transaction_not_found(self):
        with self.assertRaises(TransactionNotFoundError):
            await self.detector.detect(
                "0000000000000000000000000000000000000000000000000000000000000000"
            )

    async def test_propagates_provider_error(self):
        provider = EsploraProvider("", use_async=True)
        detector = Detector(provider)

        with self.assertRaises(ProviderError):
            await detector.detect(POTENTIAL_PAYJOIN_TX)


class TestDetectBlock(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.provider = EsploraProvider(API, use_async=True)
        self.detector = Detector(self.provider)
        self.result = await self.detector.detect_block(BLOCK_HASH)

    async def test_returns_block_detection_result(self):
        self.assertIsInstance(self.result, BlockDetectionResult)

    async def test_total_txs_count(self):
        self.assertEqual(self.result.total_txs, 2)

    async def test_blockhash_preserved(self):
        self.assertEqual(self.result.blockhash, BLOCK_HASH)

    async def test_threshold_default_is_0_1(self):
        self.assertEqual(self.result.threshold, 0.1)

    async def test_results_list_length_matches_total_txs(self):
        self.assertEqual(len(self.result.results), self.result.total_txs)


if __name__ == "__main__":
    unittest.main()
