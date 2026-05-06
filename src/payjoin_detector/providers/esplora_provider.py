"""
HTTP provider for any Esplora-compatible API.
"""

import asyncio
import urllib.request
import urllib.error
import json

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

    async def get_outspend(self, txid: str, vout: int) -> dict:
        url = f"{self.base_url}/tx/{txid}/outspends"

        def fetch():
            with urllib.request.urlopen(url, timeout=10) as resp:
                return json.load(resp)

        outspends = await asyncio.to_thread(fetch)

        if vout < 0 or vout >= len(outspends):
            raise IndexError(f"vout {vout} out of range")

        return outspends[vout]
