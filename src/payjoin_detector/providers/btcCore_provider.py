"""
JSON-RPC provider for a Bitcoin Core node.
"""

import asyncio
import urllib.request
import urllib.error
import json
import base64

from payjoin_detector.core.transaction import (
    PrevOut,
    Transaction,
    TxInput,
    TxOutput,
    TxStatus,
)
from payjoin_detector.core.provider import (
    TransactionProvider,
    TransactionNotFoundError,
    BlockNotFoundError,
    ProviderError,
)


class BitcoinCoreProvider(TransactionProvider):
    """
    Fetches transactions from a Bitcoin Core node via JSON-RPC.

    Requires txindex=1 in bitcoin.conf to look up arbitrary transactions.

    Args:
        rpc_url:        Full RPC URL, e.g. "http://127.0.0.1:8332"
        rpc_user:       RPC username
        rpc_password:   RPC password
        timeout:        HTTP request timeout in seconds
        use_async:      If True, fetch transactions in parallel. Defaults to False.
    """

    def __init__(
        self,
        rpc_url: str = "",
        rpc_user: str = "",
        rpc_password: str = "",
        timeout: int = 10,
        use_async: bool = False,
    ):
        self.rpc_url = rpc_url.rstrip("/")
        self._auth = base64.b64encode(f"{rpc_user}:{rpc_password}".encode()).decode()
        self.timeout = timeout
        self.use_async = use_async
        self._id = 0

    async def get_transaction(self, txid: str) -> Transaction:
        raw = await asyncio.to_thread(self._rpc_getrawtransaction, txid)
        return self._parse(raw)

    async def get_transactions(self, txids: list[str]) -> list[Transaction]:
        """
        Fetch and parse multiple transactions by txid.

        Args:
            txids: List of transaction IDs to fetch

        Returns:
            List of Transaction objects
        """
        transactions = []
        for txid in txids:
            try:
                tx = await self.get_transaction(txid)
                transactions.append(tx)
            except (TransactionNotFoundError, ProviderError) as e:
                raise e
        return transactions

    async def get_block_transactions(self, block_hash: str) -> list[Transaction]:
        """
        Fetch all transactions from a block_hash.

        Args:
            block_hash: The block hash to fetch transactions from

        Returns:
            List of Transaction objects
        """
        block = await asyncio.to_thread(self._rpc_getblock, block_hash, verbosity=3)
        return [self._parse(raw) for raw in block["tx"]]

    def _call(self, method: str, params: list) -> dict:
        """Send one JSON-RPC call, return the 'result' field."""
        self._id += 1
        payload = json.dumps(
            {
                "id": self._id,
                "method": method,
                "params": params,
            }
        ).encode()

        req = urllib.request.Request(
            self.rpc_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {self._auth}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="replace")
            try:
                body = json.loads(body_text)
            except Exception:
                raise ProviderError(f"HTTP {e.code}: {body_text}") from e
        except Exception as e:
            raise ProviderError(f"RPC request failed: {e}") from e

        if body.get("error"):
            err = body["error"]
            code = err.get("code", 0)
            msg = err.get("message", str(err))
            # -5 = invalid or non-wallet tx, -8 = block not found
            if code == -5:
                raise TransactionNotFoundError(msg)
            if code == -8:
                raise BlockNotFoundError(msg)
            raise ProviderError(f"RPC error {code}: {msg}")

        return body["result"]

    def _rpc_getrawtransaction(self, txid: str) -> dict:
        raw = self._call("getrawtransaction", [txid, True])
        for vin in raw.get("vin", []):
            if "coinbase" in vin:
                continue
            try:
                prev_tx = self._call("getrawtransaction", [vin["txid"], True])
                vin["prevout"] = prev_tx["vout"][vin["vout"]]
            except (ProviderError, TransactionNotFoundError, KeyError, IndexError):
                vin["prevout"] = None
        return raw

    def _rpc_getblock(self, block_hash: str, verbosity: int = 1) -> dict:
        return self._call("getblock", [block_hash, verbosity])

    def _parse(self, raw: dict) -> Transaction:
        inputs = []
        input_value = 0
        for vin in raw.get("vin", []):
            is_coinbase = "coinbase" in vin
            prevout = None

            if not is_coinbase:
                prev = vin.get("prevout")
                if prev:
                    spk = prev.get("scriptPubKey", {})
                    prevout = PrevOut(
                        value=int(round(prev.get("value", 0) * 1e8)),
                        scriptpubkey=spk.get("hex", ""),
                        scriptpubkey_asm=spk.get("asm", ""),
                        scriptpubkey_type=spk.get("type", "unknown"),
                        scriptpubkey_address=(
                            spk.get("address") or (spk.get("addresses") or [None])[0]
                        ),
                    )
                    input_value += prevout.value

            inputs.append(
                TxInput(
                    txid=vin.get("txid", 64 * "0"),
                    vout=vin.get("vout", 0),
                    scriptsig=vin.get("scriptSig", {}).get("hex", ""),
                    scriptsig_asm=vin.get("scriptSig", {}).get("asm", ""),
                    witness=vin.get("txinwitness", []),
                    is_coinbase=is_coinbase,
                    sequence=vin.get("sequence", 0xFFFFFFFF),
                    prevout=prevout,
                )
            )

        outputs = []
        for vout in raw.get("vout", []):
            spk = vout.get("scriptPubKey", {})
            outputs.append(
                TxOutput(
                    value=int(round(vout.get("value", 0) * 1e8)),
                    scriptpubkey=spk.get("hex", ""),
                    scriptpubkey_asm=spk.get("asm", ""),
                    scriptpubkey_type=spk.get("type", "unknown"),
                    scriptpubkey_address=(
                        spk.get("address") or (spk.get("addresses") or [""])[0]
                    ),
                )
            )
        output_value = sum(vout.value for vout in outputs)

        confirmed = raw.get("confirmations", 0) > 0
        block_hash = raw.get("blockhash", "")
        block_time = raw.get("blocktime", 0)
        block_height = raw.get("height", 0)

        status = TxStatus(
            confirmed=confirmed,
            block_height=block_height,
            block_hash=block_hash,
            block_time=block_time,
        )

        return Transaction(
            txid=raw["txid"],
            version=raw.get("version", 1),
            locktime=raw.get("locktime", 0),
            inputs=inputs,
            outputs=outputs,
            size=raw.get("size", 0),
            weight=raw.get("weight", 0),
            fee=max(input_value - output_value, 0),
            sigops=0,
            status=status,
        )
