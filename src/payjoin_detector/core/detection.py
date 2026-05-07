from dataclasses import dataclass
from payjoin_detector.core.heuristic import HeuristicResult


@dataclass
class TxDetectionResult:
    txid: str
    input_count: int
    output_count: int
    confidence: float
    heuristics: list[str]
    heuristics_results: list[HeuristicResult] | None = None


@dataclass
class BlockDetectionResult:
    blockhash: str
    total_txs: int
    above_threshold: int
    threshold: float
    results: list[TxDetectionResult]
