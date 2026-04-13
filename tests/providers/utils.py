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

BLOCK_170_TX_2 = Transaction(
    txid="f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16",
    version=1,
    locktime=0,
    inputs=[
        TxInput(
            txid="0437cd7f8525ceed2324359c2d0ba26006d92d856a9c20fa0241106ee5a597c9",
            vout=0,
            scriptsig="47304402204e45e16932b8af514961a1d3a1a25fdf3f4f7732e9d624c6c61548ab5fb8cd410220181522ec8eca07de4860a4acdd12909d831cc56cbbac4622082221a8768d1d0901",
            scriptsig_asm="OP_PUSHBYTES_71 304402204e45e16932b8af514961a1d3a1a25fdf3f4f7732e9d624c6c61548ab5fb8cd410220181522ec8eca07de4860a4acdd12909d831cc56cbbac4622082221a8768d1d0901",
            witness=[],
            is_coinbase=False,
            sequence=4294967295,
            prevout=PrevOut(
                scriptpubkey="410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3ac",
                scriptpubkey_asm="OP_PUSHBYTES_65 0411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3 OP_CHECKSIG",
                scriptpubkey_type="p2pk",
                scriptpubkey_address=None,
                value=5000000000,
            ),
        )
    ],
    outputs=[
        TxOutput(
            value=1000000000,
            scriptpubkey="4104ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6cd84cac",
            scriptpubkey_asm="OP_PUSHBYTES_65 04ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6cd84c OP_CHECKSIG",
            scriptpubkey_type="p2pk",
            scriptpubkey_address="",
        ),
        TxOutput(
            value=4000000000,
            scriptpubkey="410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3ac",
            scriptpubkey_asm="OP_PUSHBYTES_65 0411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3 OP_CHECKSIG",
            scriptpubkey_type="p2pk",
            scriptpubkey_address="",
        ),
    ],
    size=275,
    weight=1100,
    fee=0,
    sigops=8,
    status=TxStatus(
        confirmed=True,
        block_height=170,
        block_hash="00000000d1145790a8694403d4063f323d499e655c83426834d4ce2f8dd4a2ee",
        block_time=1231731025,
    ),
)

BLOCK_170_TX_1 = Transaction(
    txid="b1fea52486ce0c62bb442b530a3f0132b826c74e473d1f2c220bfa78111c5082",
    version=1,
    locktime=0,
    inputs=[
        TxInput(
            txid="0000000000000000000000000000000000000000000000000000000000000000",
            vout=4294967295,
            scriptsig="04ffff001d0102",
            scriptsig_asm="OP_PUSHBYTES_4 ffff001d OP_PUSHBYTES_1 02",
            witness=[],
            is_coinbase=True,
            sequence=4294967295,
            prevout=None,
        )
    ],
    outputs=[
        TxOutput(
            value=5000000000,
            scriptpubkey="4104d46c4968bde02899d2aa0963367c7a6ce34eec332b32e42e5f3407e052d64ac625da6f0718e7b302140434bd725706957c092db53805b821a85b23a7ac61725bac",
            scriptpubkey_asm="OP_PUSHBYTES_65 04d46c4968bde02899d2aa0963367c7a6ce34eec332b32e42e5f3407e052d64ac625da6f0718e7b302140434bd725706957c092db53805b821a85b23a7ac61725b OP_CHECKSIG",
            scriptpubkey_type="p2pk",
            scriptpubkey_address="",
        )
    ],
    size=134,
    weight=536,
    fee=0,
    sigops=4,
    status=TxStatus(
        confirmed=True,
        block_height=170,
        block_hash="00000000d1145790a8694403d4063f323d499e655c83426834d4ce2f8dd4a2ee",
        block_time=1231731025,
    ),
)

SIMPLE_BLOCK_HASH = "00000000d1145790a8694403d4063f323d499e655c83426834d4ce2f8dd4a2ee"

TX_IDS = [
    "b1fea52486ce0c62bb442b530a3f0132b826c74e473d1f2c220bfa78111c5082",
    "f4184fc596403b9d638783cf57adfe4c75c605f6356fbc91338530e9831e9e16",
]


def assert_tx_equal(self, tx: Transaction, expected: Transaction):
    self.assertEqual(tx.txid, expected.txid)
    self.assertEqual(tx.version, expected.version)
    self.assertEqual(tx.locktime, expected.locktime)

    self.assertEqual(tx.fee, expected.fee)
    self.assertEqual(tx.weight, expected.weight)
    self.assertEqual(tx.size, expected.size)

    self.assertEqual(len(tx.inputs), len(expected.inputs))
    self.assertEqual(len(tx.outputs), len(expected.outputs))


def assert_inputs_equal(self, tx: Transaction, expected: Transaction):
    for a, b in zip(tx.inputs, expected.inputs):
        if a.is_coinbase or b.is_coinbase:
            self.assertTrue(a.is_coinbase)
            self.assertTrue(b.is_coinbase)
            continue

        self.assertEqual(a.txid, b.txid)
        self.assertEqual(a.vout, b.vout)
        self.assertEqual(a.scriptsig, b.scriptsig)
        self.assertEqual(a.sequence, b.sequence)

        if a.prevout is not None or b.prevout is not None:
            self.assertIsNotNone(a.prevout)
            self.assertIsNotNone(b.prevout)

            self.assertEqual(a.prevout.value, b.prevout.value)
            self.assertEqual(a.prevout.scriptpubkey, b.prevout.scriptpubkey)
            self.assertEqual(
                a.prevout.scriptpubkey_address,
                b.prevout.scriptpubkey_address,
            )


def assert_outputs_equal(self, tx, expected):
    for a, b in zip(tx.outputs, expected.outputs):
        self.assertEqual(a.value, b.value)
        self.assertEqual(a.scriptpubkey, b.scriptpubkey)
        self.assertEqual(a.scriptpubkey_address, b.scriptpubkey_address)
