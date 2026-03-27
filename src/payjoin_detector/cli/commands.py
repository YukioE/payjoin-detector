from payjoin_detector.detector import Detector
from payjoin_detector.cli.printer import print_block_result, print_single_result
from payjoin_detector.core.provider import (
    BlockNotFoundError,
    ProviderError,
    TransactionNotFoundError,
)


def cmd_tx(args, detector: Detector) -> None:
    try:
        result = detector.detect(args.txid)
    except TransactionNotFoundError:
        print(f"Error: transaction {args.txid!r} not found.")
        return
    except ProviderError as e:
        print(f"Error fetching transaction: {e}")
        return

    print_single_result(result)


def cmd_block(args, detector: Detector) -> None:
    try:
        block_result = detector.detect_block(args.blockhash)
    except BlockNotFoundError:
        print(f"Error: block {args.blockhash!r} not found.")
        return
    except ProviderError as e:
        print(f"Error fetching block: {e}")
        return

    print_block_result(block_result)
