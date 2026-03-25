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
    scriptpubkey_address: str
    value: int


@dataclass
class TxInput:
    txid: str
    vout: int
    scriptsig: str | None
    scriptsig_asm: str | None
    witness: list[str] | None
    is_coinbase: bool
    sequence: int
    prevout: PrevOut | None


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
    block_height: int | None
    block_hash: str | None
    block_time: int | None


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
    sigops: int | None
