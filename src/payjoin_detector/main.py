#!/usr/bin/env python3
"""
Usage:
    python main.py tx    <txhash>
    python main.py block <blockhash>
"""

import argparse
from payjoin_detector.cli.commands import cmd_block, cmd_tx
from payjoin_detector.detector import Detector
from payjoin_detector.providers.esplora_provider import EsploraProvider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PayJoin detector")

    subparsers = parser.add_subparsers(dest="command", required=True)

    tx_parser = subparsers.add_parser("tx", help="Analyze single transaction")
    tx_parser.add_argument("txid", help="Transaction ID")

    block_parser = subparsers.add_parser("block", help="Analyze block")
    block_parser.add_argument("blockhash", help="Block hash")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    provider = EsploraProvider()
    detector = Detector(provider=provider)

    if args.command == "tx":
        cmd_tx(args, detector)
    elif args.command == "block":
        cmd_block(args, detector)


if __name__ == "__main__":
    main()
