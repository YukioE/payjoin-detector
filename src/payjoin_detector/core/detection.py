from dataclasses import dataclass


@dataclass
class TxDetectionResult:
    txid: str
    input_count: int
    output_count: int
    confidence: float
    heuristics: list[str]


@dataclass
class BlockDetectionResult:
    blockhash: str
    total_txs: int
    above_threshold: int
    threshold: float
    results: list[TxDetectionResult]
