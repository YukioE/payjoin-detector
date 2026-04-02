"""
Public library API for payjoin detection.
"""

from payjoin_detector.core.provider import TransactionProvider
from payjoin_detector.detector import Detector
from payjoin_detector.providers.esplora_provider import EsploraProvider


def analyse_txid(txid: str, provider: TransactionProvider | None = None) -> float:
    """
    Fetch a transaction by ID and return a payjoin probability score.

    Args:
        txid:     The transaction ID to look up.
        provider: A TransactionProvider used to fetch the transaction.
                  Defaults to EsploraProvider if not specified.

    Returns:
        A float in [0.0, 1.0] — higher means more likely to be a payjoin.

    Raises:
        TransactionNotFoundError: if the txid doesn't exist.
        ProviderError:            on any other network/provider failure.
    """
    detector = Detector(provider=provider or EsploraProvider())
    return detector.detect(txid).confidence


def analyse_block(
    block_hash: str,
    provider: TransactionProvider | None = None,
    threshold: float = 0.1,
) -> dict[str, float]:
    """
    Analyse all transactions in a block and return a payjoin probability
    score for each.

    Args:
        block_hash: The block hash to analyse.
        provider:   A TransactionProvider. Defaults to EsploraProvider.
        threshold:  Only return transactions at or above this confidence.
                    Defaults to 0.1. Pass 0.0 to get all transactions.

    Returns:
        A dict mapping txid -> confidence for transactions above threshold.

    Raises:
        BlockNotFoundError: if the block hash doesn't exist.
        ProviderError:      on any other network/provider failure.
    """
    detector = Detector(provider=provider or EsploraProvider())
    block_result = detector.detect_block(block_hash, threshold=threshold)
    return {
        r.txid: r.confidence for r in block_result.results if r.confidence >= threshold
    }
