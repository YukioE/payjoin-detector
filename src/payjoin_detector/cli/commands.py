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


async def cmd_block(args, detector: Detector) -> None:
    try:
        block_result = await detector.detect_block(
            args.blockhash,
            threshold=getattr(args, "threshold", 0.1),
            use_async=getattr(args, "use_async", False),
        )
    except BlockNotFoundError:
        print(f"Error: block {args.blockhash!r} not found.")
        return
    except ProviderError as e:
        print(f"Error fetching block: {e}")
        return

    print_block_result(block_result)
