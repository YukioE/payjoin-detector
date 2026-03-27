#!/usr/bin/env python3
"""
Usage:
    python main.py tx    <txhash>
    python main.py block <blockhash>
"""

import argparse
from payjoin_detector.detector import BlockDetectionResult, Detector, TxDetectionResult
from payjoin_detector.esplora_provider import EsploraProvider
from payjoin_detector.provider import (
    BlockNotFoundError,
    ProviderError,
    TransactionNotFoundError,
)


def _print_single_result(result: TxDetectionResult) -> None:
    print(f"\nTX         : {result.txid}")
    print(f"Inp/Out    : {result.input_count} / {result.output_count}")
    print(f"Confidence : {result.confidence:.2%}")
    for s in result.heuristics:
        print(f"  {s}")
    print()


def _print_block_result(block: BlockDetectionResult) -> None:
    print(f"\nBlock      : {block.blockhash}")
    print("-" * 60)
    print(f"Total txs       : {block.total_txs}")
    print(
        f"Above threshold : {block.above_threshold} "
        f"({(block.above_threshold / block.total_txs * 100) if block.total_txs else 0:.1f}%) "
        f"[>= {block.threshold:.0%}]"
    )
    print("-" * 60)

    filtered = [r for r in block.results if r.confidence >= block.threshold]

    if not filtered:
        print("\nNo transactions met the threshold.\n")
        return

    filtered.sort(key=lambda r: r.confidence, reverse=True)

    print(f"\nResults ({len(filtered)} txs):\n")

    for result in filtered:
        _print_single_result(result)


def cmd_tx(args, detector: Detector) -> None:
    try:
        result = detector.detect(args.txid)
    except TransactionNotFoundError:
        print(f"Error: transaction {args.txid!r} not found.")
        return
    except ProviderError as e:
        print(f"Error fetching transaction: {e}")
        return

    _print_single_result(result)


def cmd_block(args, detector: Detector) -> None:
    try:
        block_result = detector.detect_block(args.blockhash)
    except BlockNotFoundError:
        print(f"Error: block {args.blockhash!r} not found.")
        return
    except ProviderError as e:
        print(f"Error fetching block: {e}")
        return

    _print_block_result(block_result)


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
