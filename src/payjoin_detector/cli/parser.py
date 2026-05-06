import argparse
import sys
import tomllib
from pathlib import Path
from payjoin_detector.core import provider
from payjoin_detector.providers.btcCore_provider import BitcoinCoreProvider
from payjoin_detector.providers.esplora_provider import EsploraProvider


def _load_config(path: str | None) -> dict:
    """Return a (possibly empty) dict from a TOML config file."""
    if path is None:
        return {}
    p = Path(path)
    if not p.exists():
        print(f"Error: config file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with p.open("rb") as fh:
        return tomllib.load(fh)


def _apply_config(args: argparse.Namespace, cfg: dict) -> None:
    """
    Fill in every unset CLI arg from the config file.
    CLI values have priority, config is only used when the arg is still None / its default.
    """
    prov = cfg.get("provider", {})
    esplora = cfg.get("esplora", {})
    core = cfg.get("bitcoin_core", {})
    block = cfg.get("block", {})
    output = cfg.get("output", {})

    # csv output
    if args.csv_output is None and "csv_file" in output:
        args.csv_output = output["csv_file"]

    if args.debug_output is None and "debug_file" in output:
        args.debug_output = output["debug_file"]

    # provider type
    if args.provider == "esplora" and "type" in prov:
        args.provider = prov["type"]

    # async
    if not args.use_async and "async" in prov:
        args.use_async = prov["async"]

    # esplora
    if args.esplora_url is None and "url" in esplora:
        args.esplora_url = esplora["url"]

    # bitcoin-core
    if args.rpc_url is None and "rpc_url" in core:
        args.rpc_url = core["rpc_url"]
    if args.rpc_user is None and "rpc_user" in core:
        args.rpc_user = core["rpc_user"]
    if args.rpc_password is None and "rpc_password" in core:
        args.rpc_password = core["rpc_password"]

    # block-specific
    if hasattr(args, "threshold") and args.threshold == 0.1 and "threshold" in block:
        args.threshold = block["threshold"]


def _add_provider_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--provider",
        choices=["esplora", "bitcoin-core"],
        default="esplora",
    )
    p.add_argument(
        "--config",
        default=None,
        metavar="FILE",
        help="Path to a TOML config file (e.g. payjoin_detector.toml)",
    )
    p.add_argument(
        "--async",
        dest="use_async",
        action="store_true",
        help="Fetch transactions in parallel",
    )
    p.add_argument(
        "--csv-output",
        default=None,
        metavar="FILE",
        help="Write txid,confidence rows to this CSV file (appends if file exists)",
    )
    p.add_argument(
        "--debug-output",
        default=None,
        metavar="FILE",
        help="Write debug logs to this file",
    )

    esplora_group = p.add_argument_group("Esplora options")
    esplora_group.add_argument(
        "--esplora-url", default=None, help="Base URL — e.g. https://mempool.space/api"
    )

    core_group = p.add_argument_group("Bitcoin Core options")
    core_group.add_argument("--rpc-url", default=None)
    core_group.add_argument("--rpc-user", default=None)
    core_group.add_argument("--rpc-password", default=None)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PayJoin detector")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tx_parser = subparsers.add_parser("tx", help="Analyze single transaction")
    tx_parser.add_argument("txid", help="Transaction ID")
    _add_provider_args(tx_parser)

    block_parser = subparsers.add_parser("block", help="Analyze block")
    block_parser.add_argument("blockhash", help="Block hash")
    block_parser.add_argument("--threshold", type=float, default=0.1, metavar="0.0-1.0")
    _add_provider_args(block_parser)

    prop_parser = subparsers.add_parser(
        "propagation", help="Inter-transaction propagation analysis"
    )
    prop_parser.add_argument("txid", help="Transaction ID")
    _add_provider_args(prop_parser)

    return parser


def get_provider(args: argparse.Namespace) -> provider.TransactionProvider:
    """Parse --config (if given), merge into args, then build the provider."""
    cfg = _load_config(getattr(args, "config", None))
    _apply_config(args, cfg)

    use_async = getattr(args, "use_async", False)

    if args.provider == "bitcoin-core":
        missing = [
            name
            for name, val in [
                ("--rpc-url", args.rpc_url),
                ("--rpc-user", args.rpc_user),
                ("--rpc-password", args.rpc_password),
            ]
            if not val
        ]
        if missing:
            print("Error: bitcoin-core provider requires:", file=sys.stderr)
            for m in missing:
                print(f"  {m}", file=sys.stderr)
            sys.exit(1)
        return BitcoinCoreProvider(
            rpc_url=args.rpc_url,
            rpc_user=args.rpc_user,
            rpc_password=args.rpc_password,
            use_async=use_async,
        )

    if args.esplora_url:
        return EsploraProvider(args.esplora_url, use_async=use_async)
    return EsploraProvider(use_async=use_async)
