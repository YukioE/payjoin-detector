"""
Abstract base class for transaction providers.
"""

from abc import ABC, abstractmethod
from payjoin_detector.core.transaction import Transaction


class TransactionProvider(ABC):
    """
    Fetch and normalize a transaction from any source.
    """

    supports_clustering: bool = False

    @abstractmethod
    async def get_transaction(self, txid: str) -> Transaction:
        """
        Fetch a transaction by txid.
        Raises TransactionNotFoundError if the txid is unknown.
        Raises ProviderError on network / parsing failure.
        """
        ...

    @abstractmethod
    async def get_transactions(
        self, block_hash: str, use_async: bool = False
    ) -> list[Transaction]:
        """
        Fetch all transactions from a block_hash.
        Raises BlockNotFoundError if the block_hash is unknown.
        Raises TransactionNotFoundError if a txid is unknown.
        Raises ProviderError on network / parsing failure.
        """
        ...

    async def get_cluster_transactions(
        self, tx: Transaction, depth: int = 1, max_txs_per_address: int = 50
    ) -> list[Transaction]:
        """
        Fetch all transactions needed for CIOH clustering.
        Walks the transaction graph up to `depth` hops from each input address.
        Raises ProviderError on network / parsing failure.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support clustering"
        )

    def _get_address_txids(self, address: str, max_txs: int) -> list[str]:
        """
        Fetch paginated transaction IDs for a given address.
        Raises ProviderError on network / parsing failure.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support clustering"
        )


class TransactionNotFoundError(Exception):
    pass


class BlockNotFoundError(Exception):
    pass


class ProviderError(Exception):
    pass
