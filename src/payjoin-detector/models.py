"""
Core data models for payjoin detection.
Creating an adapter for any API should result in these types
"""

from dataclasses import dataclass
from typing import Optional


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
    prevout: PrevOut
    scriptsig: str
    scriptsig_asm: str
    witness: list[str]
    is_coinbase: bool
    sequence: int


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
    block_height: int
    block_hash: str
    block_time: int


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
    sigops: Optional[int] = None


@dataclass
class DetectionResult:
    txid: str
    confidence: float
    signals: list[str]
