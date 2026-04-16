import argparse
import sys

from payjoin_detector.core import provider
from payjoin_detector.providers.btcCore_provider import BitcoinCoreProvider
from payjoin_detector.providers.esplora_provider import EsploraProvider


def _add_provider_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--provider",
        choices=["esplora", "bitcoin-core"],
        default="esplora",
        help="Which data provider to use",
    )

    esplora_group = p.add_argument_group("Esplora options")
    esplora_group.add_argument(
        "--esplora-url",
        default=None,
        help="Base URL for the Esplora API - e.g.: https://mempool.space/api",
    )

    core_group = p.add_argument_group("Bitcoin Core options")
    core_group.add_argument(
        "--rpc-url",
        default=None,
        help="RPC URL",
    )
    core_group.add_argument(
        "--rpc-user",
        default=None,
        help="RPC username",
    )
    core_group.add_argument(
        "--rpc-password",
        default=None,
        help="RPC password",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PayJoin detector")

    subparsers = parser.add_subparsers(dest="command", required=True)

    tx_parser = subparsers.add_parser("tx", help="Analyze single transaction")
    tx_parser.add_argument("txid", help="Transaction ID")
    _add_provider_args(tx_parser)

    block_parser = subparsers.add_parser("block", help="Analyze block")
    block_parser.add_argument("blockhash", help="Block hash")
    block_parser.add_argument(
        "--threshold",
        type=float,
        default=0.1,
        metavar="0.0-1.0",
        help="Minimum heuristic score [0.0–1.0] to flag a transaction",
    )
    block_parser.add_argument(
        "--async",
        dest="use_async",
        action="store_true",
        help="Fetch block transactions concurrently (faster, more connections)",
    )
    _add_provider_args(block_parser)

    return parser


def get_provider(args: argparse.Namespace) -> provider.TransactionProvider:
    if args.provider == "bitcoin-core":
        rpc_url = args.rpc_url
        rpc_user = args.rpc_user
        rpc_pass = args.rpc_password

        missing = [
            name
            for name, val in [
                ("--rpc-url", rpc_url),
                ("--rpc-user", rpc_user),
                ("--rpc-password", rpc_pass),
            ]
            if not val
        ]

        if missing:
            print("Error: bitcoin-core provider requires:", file=sys.stderr)
            for m in missing:
                print(f"  {m}", file=sys.stderr)
            sys.exit(1)

        return BitcoinCoreProvider(
            rpc_url=rpc_url, rpc_user=rpc_user, rpc_password=rpc_pass
        )

    return EsploraProvider(args.esplora_url) if args.esplora_url else EsploraProvider()
