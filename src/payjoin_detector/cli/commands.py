from pathlib import Path
import csv
from payjoin_detector.detector import Detector
from payjoin_detector.cli.printer import print_block_result, print_single_result
from payjoin_detector.core.provider import (
    BlockNotFoundError,
    ProviderError,
    TransactionNotFoundError,
)


async def cmd_tx(args, detector: Detector) -> None:
    try:
        result = await detector.detect(args.txid)
    except TransactionNotFoundError:
        print(f"Error: transaction {args.txid!r} not found.")
        return
    except ProviderError as e:
        print(f"Error fetching transaction: {e}")
        return

    print_single_result(result)
    if getattr(args, "csv_output", None):
        _write_csv(args.csv_output, [(result.txid, result.confidence)])


async def cmd_block(args, detector: Detector) -> None:
    threshold = getattr(args, "threshold", 0.1)
    try:
        block_result = await detector.detect_block(
            args.blockhash,
            threshold,
            use_async=getattr(args, "use_async", False),
        )
    except BlockNotFoundError:
        print(f"Error: block {args.blockhash!r} not found.")
        return
    except ProviderError as e:
        print(f"Error fetching block: {e}")
        return

    print_block_result(block_result)
    if getattr(args, "csv_output", None):
        rows = [
            (r.txid, r.confidence)
            for r in block_result.results
            if r.confidence >= threshold
        ]
        _write_csv(args.csv_output, rows)


def _write_csv(path: str, rows: list[tuple[str, float]]) -> None:
    """Append txid,confidence rows to a CSV file, writing a header if new."""
    p = Path(path)
    write_header = not p.exists() or p.stat().st_size == 0
    with p.open("a", newline="") as fh:
        writer = csv.writer(fh)
        if write_header:
            writer.writerow(["txid", "confidence"])
        writer.writerows(rows)
