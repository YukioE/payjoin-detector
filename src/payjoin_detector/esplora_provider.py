"""
HTTP provider for any Esplora-compatible API.
"""

import urllib.request
import urllib.error
import json

from payjoin_detector.transaction import (
    Transaction,
    TxInput,
    TxOutput,
    TxStatus,
    PrevOut,
)
from payjoin_detector.provider import (
    TransactionProvider,
    TransactionNotFoundError,
    ProviderError,
)

MEMPOOL_BASE = "https://mempool.space/api"
BLOCKSTREAM_BASE = "https://blockstream.info/api"


class EsploraProvider(TransactionProvider):
    """
    Fetches transactions from any Esplora REST API.

    Args:
        base_url: Root URL of the Esplora API, no trailing slash.
        timeout:  HTTP request timeout in seconds.
    """

    def __init__(self, base_url: str = MEMPOOL_BASE, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_transaction(self, txid: str) -> Transaction:
        raw = self._fetch_json(f"{self.base_url}/tx/{txid}")
        return self._parse(raw)

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
