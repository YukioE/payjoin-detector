import unittest

from payjoin_detector.core import provider
from payjoin_detector.providers.esplora_provider import EsploraProvider
from payjoin_detector.core.transaction import (
    PrevOut,
    Transaction,
    TxInput,
    TxOutput,
    TxStatus,
)

SIMPLE_TX = Transaction(
    txid="fe392c348ba83afe4adfd2f911a8fa78498f49c835bdb90b883b730a8b096968",
    version=1,
    locktime=0,
    inputs=[
        TxInput(
            txid="3ca93b1d3eab820e8a650b6dc8f743d1f2066e386335d6cda8df6099b50c12e8",
            vout=0,
            scriptsig="483045022100ef8137745ccbc558066a05e02222f2d1516b3f099097e9a5642db296c218d89802202824d273a90478def3cb7401c258682ee1bcd0228a0e0bb98000d093c72acd2a0121039dca31867355ea3421afc42f2b8293c6869808c4ef8708b7369184a9984bb0fb",
            scriptsig_asm="OP_PUSHBYTES_72 3045022100ef8137745ccbc558066a05e02222f2d1516b3f099097e9a5642db296c218d89802202824d273a90478def3cb7401c258682ee1bcd0228a0e0bb98000d093c72acd2a01 OP_PUSHBYTES_33 039dca31867355ea3421afc42f2b8293c6869808c4ef8708b7369184a9984bb0fb",
            witness=[],
            is_coinbase=False,
            sequence=4294967295,
            prevout=PrevOut(
                scriptpubkey="76a914396a2226bf3b865f7aa3d8a2b581e87e0803f22588ac",
                scriptpubkey_asm="OP_DUP OP_HASH160 OP_PUSHBYTES_20 396a2226bf3b865f7aa3d8a2b581e87e0803f225 OP_EQUALVERIFY OP_CHECKSIG",
                scriptpubkey_type="p2pkh",
                scriptpubkey_address="16EafDKsHEWk6CEHyWCj9QryZZYhNU368z",
                value=1387507,
            ),
        )
    ],
    outputs=[
        TxOutput(
            value=1300207,
            scriptpubkey="76a9145a0b5d304da68a522b0c6e8179344e44f584620688ac",
            scriptpubkey_asm="OP_DUP OP_HASH160 OP_PUSHBYTES_20 5a0b5d304da68a522b0c6e8179344e44f5846206 OP_EQUALVERIFY OP_CHECKSIG",
            scriptpubkey_type="p2pkh",
            scriptpubkey_address="19D7RrLKjWSBwxQfxJqZ1CnohCFy9TzFjz",
        )
    ],
    size=192,
    weight=768,
    fee=87300,
    sigops=4,
    status=TxStatus(
        confirmed=True,
        block_height=500000,
        block_hash="00000000000000000024fb37364cbf81fd49cc2d51c09c75c35433c3a1945d04",
        block_time=1513622125,
    ),
)

SIMPLE_BLOCK_HASH = "00000000d1145790a8694403d4063f323d499e655c83426834d4ce2f8dd4a2ee"

TX_IDS = [
    "b1fea52486ce0c62bb442b530a3f0132b826c74e473d1f2c220bfa78111c5082",
    "f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16",
]


class TestGetTransaction(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.provider = EsploraProvider()

    async def test_returns_transaction(self):
        tx = await self.provider.get_transaction(SIMPLE_TX.txid)
        self.assertIsInstance(tx, Transaction)
        self.assertEqual(tx, SIMPLE_TX)


class TestGetTransactions(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.provider = EsploraProvider()

    async def test_returns_transactions(self):
        txs = await self.provider.get_transactions(SIMPLE_BLOCK_HASH)

        self.assertIsInstance(txs, list)
        self.assertEqual(len(txs), 2)
        self.assertTrue(all(isinstance(tx, Transaction) for tx in txs))


class TestFetchBlockTxIds(unittest.TestCase):
    def setUp(self):
        self.provider = EsploraProvider()

    def test_returns_txids(self):
        txid_list = self.provider._fetch_block_txids(SIMPLE_BLOCK_HASH)

        self.assertIsInstance(txid_list, list)
        self.assertEqual(txid_list, TX_IDS)
        self.assertTrue(all(isinstance(txid, str) for txid in txid_list))


if __name__ == "__main__":
    unittest.main()
