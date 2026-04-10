import unittest
import contextlib
import io
from payjoin_detector.main import build_parser


class TestBuildParser(unittest.TestCase):
    def test_tx_command(self):
        parser = build_parser()
        args = parser.parse_args(["tx", "0"])
        self.assertEqual(args.command, "tx")
        self.assertEqual(args.txid, "0")

    def test_block_command(self):
        parser = build_parser()
        args = parser.parse_args(["block", "0"])
        self.assertEqual(args.command, "block")
        self.assertEqual(args.blockhash, "0")

    def test_block_async_flag(self):
        parser = build_parser()
        args = parser.parse_args(["block", "0", "--async"])
        self.assertTrue(args.use_async)

    def test_async_flag_defaults_false(self):
        parser = build_parser()
        args = parser.parse_args(["block", "0"])
        self.assertFalse(args.use_async)

    def test_missing_command_exits(self):
        parser = build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args([])


if __name__ == "__main__":
    unittest.main()
