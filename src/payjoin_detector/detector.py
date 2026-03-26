"""
Detector — uses provider + heuristics to return a DetectionResult.
"""

from payjoin_detector.heuristics.coinJoin import CoinJoinHeuristic
from payjoin_detector.heuristics.nSequenceAsymmetry import NSequenceAsymmetryHeuristic
from payjoin_detector.heuristics.roundOutput import RoundOutputHeuristic
from payjoin_detector.heuristics.signatureAsymmetry import SignatureAsymmetryHeuristic
from payjoin_detector.heuristics.testh import RoundPaymentAssignmentHeuristic
from payjoin_detector.heuristics.unnecessaryInput import UnnecessaryInputHeuristic
from payjoin_detector.heuristics.mixedInputTypes import MixedInputTypesHeuristic
from payjoin_detector.heuristic import Heuristic
from payjoin_detector.provider import TransactionProvider
from payjoin_detector.transaction import Transaction
from dataclasses import dataclass


@dataclass
class DetectionResult:
    txid: str
    confidence: float
    heuristics: list[str]


DEFAULT_HEURISTICS: list[Heuristic] = [
    UnnecessaryInputHeuristic(),
    MixedInputTypesHeuristic(),
    RoundOutputHeuristic(),
    CoinJoinHeuristic(),
    NSequenceAsymmetryHeuristic(),
    SignatureAsymmetryHeuristic(),
    RoundPaymentAssignmentHeuristic(),
]


class Detector:
    """
    Main entry-point for payjoin detection.

    Args:
        provider:   Any TransactionProvider implementation.
        heuristics: List of Heuristic instances to run.
                    Defaults to DEFAULT_HEURISTICS.
    """

    def __init__(
        self,
        provider: TransactionProvider,
        heuristics: list[Heuristic] | None = None,
    ):
        self.provider = provider
        self.heuristics = heuristics if heuristics is not None else DEFAULT_HEURISTICS

    def detect(self, txid: str) -> DetectionResult:
        """Fetch tx and run all heuristics, return a DetectionResult."""
        tx = self.provider.get_transaction(txid)
        return self.analyse(tx)

    def check_payjoin_possible(self, tx: Transaction) -> bool:
        # Coinbase transactions can never be PayJoin
        if any(vin.is_coinbase for vin in tx.inputs):
            return False

        distinct_input_addrs = {
            vin.prevout.scriptpubkey_address
            for vin in tx.inputs
            if vin.prevout and vin.prevout.scriptpubkey_address
        }

        # tx must have at least 2 distinct addresses (sender & receiver)
        if len(distinct_input_addrs) < 2:
            return False

        return True

    def analyse(self, tx: Transaction) -> DetectionResult:
        """
        Run heuristics on an already-fetched Transaction.
        """
        if not self.check_payjoin_possible(tx):
            return DetectionResult(
                txid=tx.txid,
                confidence=0.0,
                heuristics=[
                    "PayJoin not possible",
                    "either Coinbase tx or <2 distinct input addresses",
                ],
            )

        results = [h.check(tx) for h in self.heuristics]
        weights = {h.name: h.weight for h in self.heuristics}

        total_weight = sum(weights[r.name] for r in results)
        weighted_score = sum(r.score * weights[r.name] for r in results)

        raw = (weighted_score / total_weight) if total_weight > 0 else 0.0
        confidence = round(max(0.0, min(1.0, raw)), 4)

        heuristic_strings = [
            f"{'[+]' if r.score > 0 else '[-]' if r.score < 0 else '[•]'} {r.name}: {r.signal}"
            for r in results
            if r.signal
        ]

        return DetectionResult(
            txid=tx.txid,
            confidence=confidence,
            heuristics=heuristic_strings,
        )
