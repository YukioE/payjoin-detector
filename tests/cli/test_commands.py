from contextlib import redirect_stdout
from types import SimpleNamespace
import unittest
import io
from payjoin_detector.cli.commands import cmd_tx, cmd_block
from payjoin_detector.detector import Detector
from payjoin_detector.providers.esplora_provider import EsploraProvider
from tests import API


TX = "f6146cbe2f7f18a62934eb338ac18762da35ad1b61aacb93eee13cb16761a1c7"
BLOCK = "00000000d1145790a8694403d4063f323d499e655c83426834d4ce2f8dd4a2ee"


class TestCmdTx(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.provider = EsploraProvider(API)
        self.detector = Detector(self.provider)
        self.args = SimpleNamespace(txid=TX)

    async def test_success(self):
        f = io.StringIO()

        with redirect_stdout(f):
            await cmd_tx(self.args, self.detector)

        output = f.getvalue()

        self.assertIn(TX, output)


class TestCmdBlock(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.provider = EsploraProvider(API)
        self.detector = Detector(self.provider)

        self.args = SimpleNamespace(blockhash=BLOCK, use_async=False)

    async def test_success(self):
        f = io.StringIO()

        with redirect_stdout(f):
            await cmd_block(self.args, self.detector)

        output = f.getvalue()

        self.assertIn("0", output)


if __name__ == "__main__":
    unittest.main()
