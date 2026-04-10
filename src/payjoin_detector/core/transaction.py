"""
Core data models for payjoin detection.
Creating an adapter for any API should result in these types
"""

from dataclasses import dataclass


@dataclass
class PrevOut:
    scriptpubkey: str
    scriptpubkey_asm: str
    scriptpubkey_type: str
    value: int
    scriptpubkey_address: str | None = None


@dataclass
class TxInput:
    txid: str
    vout: int
    is_coinbase: bool
    sequence: int
    prevout: PrevOut | None = None
    scriptsig: str | None = None
    scriptsig_asm: str | None = None
    witness: list[str] | None = None


@dataclass
class TxOutput:
    value: int
    scriptpubkey: str
    scriptpubkey_asm: str
    scriptpubkey_type: str
    scriptpubkey_address: str


@dataclass
class TxStatus:
    confirmed: bool
    block_height: int | None = None
    block_hash: str | None = None
    block_time: int | None = None


@dataclass
class Transaction:
    txid: str
    version: int
    locktime: int
    inputs: list[TxInput]
    outputs: list[TxOutput]
    size: int
    weight: int
    fee: int
    status: TxStatus
    sigops: int | None = None
