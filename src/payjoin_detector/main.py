#!/usr/bin/env python3
"""
Usage:
    python main.py <txhash>
"""

import sys

from payjoin_detector.detector import Detector
from payjoin_detector.esplora_provider import EsploraProvider
from payjoin_detector.provider import TransactionNotFoundError, ProviderError

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <txhash>", file=sys.stderr)
        sys.exit(1)

    txhash = sys.argv[1]

    # change provider here is using a different API
    provider = EsploraProvider()
    detector = Detector(provider=provider)

    try:
        result = detector.detect(txhash)
    except TransactionNotFoundError:
        print(f"Error: transaction {txhash!r} not found.", file=sys.stderr)
        sys.exit(1)
    except ProviderError as e:
        print(f"Error fetching transaction: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"\nTX         : {result.txid}")
    print(f"Confidence : {result.confidence:.1%}")
    for s in result.heuristics:
        print(f"  {s}")
    print()


if __name__ == "__main__":
    main()
