"""
HTTP provider for any Esplora-compatible API.
"""

import asyncio
import urllib.request
import urllib.error
import json

from payjoin_detector.cli.debug import get_logger
from payjoin_detector.core.transaction import (
    Transaction,
    TxInput,
    TxOutput,
    TxStatus,
    PrevOut,
)
from payjoin_detector.core.provider import (
    TransactionProvider,
    TransactionNotFoundError,
    BlockNotFoundError,
    ProviderError,
)

MEMPOOL_BASE = "https://mempool.space/api"
BLOCKSTREAM_BASE = "https://blockstream.info/api"

_MAX_CONCURRENT = 50


class EsploraProvider(TransactionProvider):
    """
    Fetches transactions from any Esplora REST API.

    Args:
        base_url:       Root URL of the Esplora API, no trailing slash.
        timeout:        HTTP request timeout in seconds.
        max_concurrent: Max parallel requests when fetching a full block.
    """

    def __init__(
        self,
        base_url: str = MEMPOOL_BASE,
        timeout: int = 10,
        max_concurrent: int = _MAX_CONCURRENT,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._sem = asyncio.Semaphore(max_concurrent)

    supports_clustering = True

    async def get_transaction(self, txid: str) -> Transaction:
        raw = await asyncio.to_thread(self._fetch_json, f"{self.base_url}/tx/{txid}")
        return self._parse(raw)

    async def get_transactions(
        self, block_hash: str, use_async: bool = False
    ) -> list[Transaction]:
        txids = await asyncio.to_thread(self._fetch_block_txids, block_hash)

        if use_async:

            async def fetch_one(txid: str) -> dict:
                async with self._sem:
                    return await asyncio.to_thread(
                        self._fetch_json, f"{self.base_url}/tx/{txid}"
                    )

            raws = await asyncio.gather(*[fetch_one(txid) for txid in txids])
        else:
            raws = []
            for txid in txids:
                raws.append(
                    await asyncio.to_thread(
                        self._fetch_json, f"{self.base_url}/tx/{txid}"
                    )
                )

        return [self._parse(raw) for raw in raws]

    def _fetch_block_txids(self, block_hash: str) -> list[str]:
        """Return the ordered list of txids for *block_hash*."""
        url = f"{self.base_url}/block/{block_hash}/txids"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "payjoin-detector/1.0"},
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise BlockNotFoundError(f"block not found: {block_hash}") from e
            raise ProviderError(
                f"HTTP {e.code} fetching txids for block {block_hash}"
            ) from e
        except Exception as e:
            raise ProviderError(f"Request failed: {e}") from e

    def _fetch_json(self, url: str) -> dict:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "payjoin-detector/1.0"},
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise TransactionNotFoundError(f"txid not found: {url}")
            raise ProviderError(f"HTTP {e.code} from {url}") from e
        except Exception as e:
            raise ProviderError(f"Request failed: {e}") from e

    def _parse(self, raw: dict) -> Transaction:
        inputs = []
        for vin in raw.get("vin", []):
            prev = vin.get("prevout")
            inputs.append(
                TxInput(
                    txid=vin.get("txid", ""),
                    vout=vin.get("vout", 0),
                    scriptsig=vin.get("scriptsig", ""),
                    scriptsig_asm=vin.get("scriptsig_asm", ""),
                    witness=vin.get("witness", []),
                    is_coinbase=vin.get("is_coinbase", False),
                    sequence=vin.get("sequence", 0xFFFFFFFF),
                    prevout=PrevOut(**prev) if prev else None,
                ),
            )

        outputs = []
        for vout in raw.get("vout", []):
            outputs.append(
                TxOutput(
                    value=vout.get("value", 0),
                    scriptpubkey=vout.get("scriptpubkey", ""),
                    scriptpubkey_asm=vout.get("scriptpubkey_asm", ""),
                    scriptpubkey_type=vout.get("scriptpubkey_type", "unknown"),
                    scriptpubkey_address=vout.get("scriptpubkey_address", ""),
                )
            )

        s = raw.get("status", {})
        status = TxStatus(
            confirmed=s.get("confirmed", False),
            block_height=s.get("block_height", 0),
            block_hash=s.get("block_hash", ""),
            block_time=s.get("block_time", 0),
        )

        return Transaction(
            txid=raw["txid"],
            version=raw.get("version", 1),
            locktime=raw.get("locktime", 0),
            inputs=inputs,
            outputs=outputs,
            size=raw.get("size", 0),
            weight=raw.get("weight", 0),
            fee=raw.get("fee", 0),
            sigops=raw.get("sigops", 0),
            status=status,
        )

    async def get_cluster_transactions(
        self, tx: Transaction, depth: int = 1, max_txs_per_address: int = 250
    ) -> list[Transaction]:
        """Fetch all transactions needed for CIOH clustering."""
        visited_addresses: set[str] = set()
        visited_txids: set[str] = set()
        result_txns: list[Transaction] = []

        current_frontier: set[str] = {
            inp.prevout.scriptpubkey_address
            for inp in tx.inputs
            if inp.prevout and inp.prevout.scriptpubkey_address
        }

        for _ in range(depth):
            new_addresses = current_frontier - visited_addresses
            if not new_addresses:
                break

            visited_addresses.update(new_addresses)

            # Fetch txids for all new addresses
            new_txids: set[str] = set()
            for addr in new_addresses:
                txs = await asyncio.to_thread(
                    self._get_address_txids, addr, max_txs_per_address
                )
                get_logger().debug(
                    "provider: fetched transaction history for clustering of address %s, %d transactions found",
                    addr,
                    len(txs),
                )
                for txid in txs:
                    new_txids.add(txid)

            new_txids -= visited_txids
            new_txids.discard(
                tx.txid
            )  # exclude target tx itself (possible payjoin cant apply CIOH)
            visited_txids.update(new_txids)

            get_logger().debug(
                "provider: found %d transactions for clustering transaction base set",
                len(new_txids),
            )

            # Fetch full transactions
            next_frontier: set[str] = set()
            for txid in new_txids:
                try:
                    txn = await self.get_transaction(txid)
                    get_logger().debug("provider: fetched %s", txid)
                    result_txns.append(txn)
                    for inp in txn.inputs:
                        if inp.prevout and inp.prevout.scriptpubkey_address:
                            next_frontier.add(inp.prevout.scriptpubkey_address)
                    for out in txn.outputs:
                        if out.scriptpubkey_address:
                            next_frontier.add(out.scriptpubkey_address)
                except Exception:
                    pass

            current_frontier = next_frontier

        return result_txns

    def _get_address_txids(self, address: str, max_txs: int) -> list[str]:
        txids: list[str] = []
        last_seen: str | None = None
        while len(txids) < max_txs:
            url = f"{self.base_url}/address/{address}/txs/chain"
            if last_seen:
                url += f"/{last_seen}"
            page = self._fetch_json(url)
            if not page:
                break
            for entry in page:
                txids.append(entry["txid"])
            if len(page) < 25:
                break
            last_seen = txids[-1]
        return txids[:max_txs]
