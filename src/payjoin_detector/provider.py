"""
Abstract base class for transaction providers.
"""

from abc import ABC, abstractmethod
from payjoin_detector.transaction import Transaction


class TransactionProvider(ABC):
    """
    Fetch and normalize a transaction from any source.
    """

    @abstractmethod
    def get_transaction(self, txid: str) -> Transaction:
        """
        Fetch a transaction by txid.
        Raises TransactionNotFoundError if the txid is unknown.
        Raises ProviderError on network / parsing failure.
        """
        ...

    @abstractmethod
    def get_transactions(self, block_hash: str) -> list[Transaction]:
        """
        Fetch all transactions from a block_hash.
        Raises BlockNotFoundError if the block_hash is unknown.
        Raises TransactionNotFoundError if a txid is unknown.
        Raises ProviderError on network / parsing failure.
        """
        ...


class TransactionNotFoundError(Exception):
    pass


class BlockNotFoundError(Exception):
    pass


class ProviderError(Exception):
    pass
