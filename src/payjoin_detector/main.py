#!/usr/bin/env python3
"""
Usage:
    python main.py tx    <txhash>
    python main.py block <blockhash>
"""

import argparse
import asyncio
import os
from payjoin_detector.cli.commands import cmd_block, cmd_tx
from payjoin_detector.detector import Detector
from payjoin_detector.providers.btcCore_provider import BitcoinCoreProvider
from payjoin_detector.providers.esplora_provider import EsploraProvider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PayJoin detector")

    subparsers = parser.add_subparsers(dest="command", required=True)

    tx_parser = subparsers.add_parser("tx", help="Analyze single transaction")
    tx_parser.add_argument("txid", help="Transaction ID")

    block_parser = subparsers.add_parser("block", help="Analyze block")
    block_parser.add_argument("blockhash", help="Block hash")
    block_parser.add_argument(
        "--async",
        dest="use_async",
        action="store_true",
        help="Fetch block transactions concurrently (faster, more connections)",
    )

    return parser


async def async_main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    provider = BitcoinCoreProvider(
        os.environ["BITCOIN_RPC_URL"],
        os.environ["BITCOIN_RPC_USER"],
        os.environ["BITCOIN_RPC_PASS"],
    )
    detector = Detector(provider=provider)

    if args.command == "tx":
        await cmd_tx(args, detector)
    elif args.command == "block":
        await cmd_block(args, detector)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
