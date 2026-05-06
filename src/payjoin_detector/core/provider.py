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
    use_async: bool = False

    @abstractmethod
    async def get_transaction(self, txid: str) -> Transaction:
        """
        Fetch a transaction by txid.
        Raises TransactionNotFoundError if the txid is unknown.
        Raises ProviderError on network / parsing failure.
        """
        ...

    @abstractmethod
    async def get_transactions(self, txids: list[str]) -> list[Transaction]:
        """
        Fetch and parse multiple transactions by txid.
        Uses self.use_async to determine parallel fetching.

        Args:
            txids: List of transaction IDs to fetch

        Returns:
            List of Transaction objects

        Raises:
            TransactionNotFoundError if a txid is unknown.
            ProviderError on network / parsing failure.
        """
        ...

    @abstractmethod
    async def get_block_transactions(self, block_hash: str) -> list[Transaction]:
        """
        Fetch all transactions from a block_hash.
        Uses self.use_async to determine parallel fetching.

        Args:
            block_hash: The block hash to fetch transactions from

        Returns:
            List of Transaction objects

        Raises:
            BlockNotFoundError if the block_hash is unknown.
            TransactionNotFoundError if a txid is unknown.
            ProviderError on network / parsing failure.
        """
        ...

    async def get_cluster_transactions(
        self,
        tx: Transaction,
        depth: int = 1,
        max_txs_per_address: int = 50,
    ) -> list[Transaction]:
        """
        Fetch all transactions needed for CIOH clustering.
        Uses self.use_async to determine parallel fetching.
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

    async def get_outspend(self, txid: str, vout: int) -> dict:
        """
        Fetches all outspend txs from a txid
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support get outspends"
        )


class TransactionNotFoundError(Exception):
    pass


class BlockNotFoundError(Exception):
    pass


class ProviderError(Exception):
    pass
