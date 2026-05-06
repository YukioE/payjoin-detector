"""
Detector — uses provider + heuristics to return a DetectionResult.
"""

from payjoin_detector.cli.debug import get_logger
from payjoin_detector.core.detection import BlockDetectionResult, TxDetectionResult
from payjoin_detector.heuristics.clustering import ClusteringHeuristic
from payjoin_detector.heuristics.roundFee import RoundFeeHeuristic
from payjoin_detector.heuristics.addressReuse import AddressReuseHeuristic
from payjoin_detector.heuristics.coinJoin import CoinJoinHeuristic
from payjoin_detector.heuristics.inputValueDisparity import InputValueDisparityHeuristic
from payjoin_detector.heuristics.mixedOutputTypes import MixedOutputTypesHeuristic
from payjoin_detector.heuristics.nSequenceAsymmetry import NSequenceAsymmetryHeuristic
from payjoin_detector.heuristics.roundOutput import RoundOutputHeuristic
from payjoin_detector.heuristics.signatureAsymmetry import SignatureAsymmetryHeuristic
from payjoin_detector.heuristics.roundPaymentAssignment import (
    RoundPaymentAssignmentHeuristic,
)
from payjoin_detector.heuristics.smallIOCounts import SmallIOCountsHeuristic
from payjoin_detector.heuristics.unnecessaryInput import UnnecessaryInputHeuristic
from payjoin_detector.heuristics.mixedInputTypes import MixedInputTypesHeuristic
from payjoin_detector.core.heuristic import Heuristic
from payjoin_detector.core.provider import TransactionProvider
from payjoin_detector.core.transaction import Transaction


DEFAULT_HEURISTICS: list[Heuristic] = [
    UnnecessaryInputHeuristic(),
    SmallIOCountsHeuristic(),
    MixedInputTypesHeuristic(),
    MixedOutputTypesHeuristic(),
    AddressReuseHeuristic(),
    RoundFeeHeuristic(),
    RoundOutputHeuristic(),
    RoundPaymentAssignmentHeuristic(),
    CoinJoinHeuristic(),
    InputValueDisparityHeuristic(),
    NSequenceAsymmetryHeuristic(),
    SignatureAsymmetryHeuristic(),
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

    async def detect(self, txid: str) -> TxDetectionResult:
        """Fetch tx and run all heuristics, return a TxDetectionResult"""
        get_logger().debug("detect: fetching txid=%s", txid)
        tx = await self.provider.get_transaction(txid)

        if self.provider.supports_clustering:
            cluster_txs = await self.provider.get_cluster_transactions(tx, depth=1)
            self.heuristics.append(ClusteringHeuristic(cluster_txs))
            get_logger().debug(
                "detect: fetched %d transactions needed for clustering",
                len(cluster_txs),
            )

        get_logger().debug(
            "detect: fetched txid=%s inputs=%d outputs=%d",
            txid,
            len(tx.inputs),
            len(tx.outputs),
        )
        result = self.analyse(tx)
        return result

    async def detect_block(
        self, block_hash: str, threshold: float = 0.1
    ) -> BlockDetectionResult:
        """Fetch all tx inside specified block and analyze each, return a BlockDetectionResult"""
        get_logger().debug(
            "detect_block: blockhash=%s threshold=%s",
            block_hash,
            threshold,
        )

        transactions = await self.provider.get_block_transactions(block_hash)
        get_logger().debug(
            "detect_block: fetched %d transactions from block=%s",
            len(transactions),
            block_hash,
        )

        results = [self.analyse(tx) for tx in transactions]

        above = [r for r in results if r.confidence >= threshold]
        get_logger().debug(
            "detect_block: block=%s total=%d above_threshold=%d (threshold=%s)",
            block_hash,
            len(results),
            len(above),
            threshold,
        )

        return BlockDetectionResult(
            blockhash=block_hash,
            total_txs=len(results),
            above_threshold=len(above),
            threshold=threshold,
            results=results,
        )

    def check_payjoin_possible(self, tx: Transaction) -> bool:
        # Coinbase transactions can never be PayJoin
        if any(vin.is_coinbase for vin in tx.inputs):
            return False

        distinct_input_addrs = {
            vin.prevout.scriptpubkey_address
            for vin in tx.inputs
            if vin.prevout and vin.prevout.scriptpubkey_address
        }

        distinct_output_addrs = {
            vout.scriptpubkey_address
            for vout in tx.outputs
            if vout.scriptpubkey_address
        }

        # tx must have at least 2 distinct addresses (sender & receiver)
        if len(distinct_input_addrs) < 2 or len(distinct_output_addrs) < 2:
            return False

        return True

    def analyse(self, tx: Transaction) -> TxDetectionResult:
        """
        Run heuristics on an already-fetched Transaction.
        """
        get_logger().debug("analyse: txid=%s", tx.txid)

        if not self.check_payjoin_possible(tx):
            return TxDetectionResult(
                txid=tx.txid,
                input_count=len(tx.inputs),
                output_count=len(tx.outputs),
                confidence=0.0,
                heuristics=[
                    "PayJoin not possible",
                    "either Coinbase tx or <2 distinct addresses",
                    "on input or output side",
                ],
            )

        results = [h.check(tx) for h in self.heuristics]
        for r in results:
            get_logger().debug(
                "analyse: heuristic=%s score=%s signal=%s",
                r.name,
                r.score,
                r.signal,
            )

        # confidence calculation: sum scores and calc average, clamp to 0.0 - 1.0, rounded percentage value to 4 digits
        raw = sum(r.score for r in results) / len(results) if results else 0.0
        confidence = round(max(0.0, min(1.0, raw)), 4)
        get_logger().debug("analyse: confidence=%s", confidence)

        heuristic_strings = [
            f"{'[+]' if r.score > 0 else '[-]' if r.score < 0 else '[ ]'} {r.name}: {r.signal}"
            for r in results
            if r.signal
        ]

        return TxDetectionResult(
            txid=tx.txid,
            input_count=len(tx.inputs),
            output_count=len(tx.outputs),
            confidence=confidence,
            heuristics=heuristic_strings,
        )
