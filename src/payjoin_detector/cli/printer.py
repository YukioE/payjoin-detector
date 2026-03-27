from payjoin_detector.detector import BlockDetectionResult, TxDetectionResult


def print_single_result(result: TxDetectionResult) -> None:
    print(f"\nTX         : {result.txid}")
    print(f"Inp/Out    : {result.input_count} / {result.output_count}")
    print(f"Confidence : {result.confidence:.2%}")
    for s in result.heuristics:
        print(f"  {s}")
    print()


def print_block_result(block: BlockDetectionResult) -> None:
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
        print_single_result(result)
