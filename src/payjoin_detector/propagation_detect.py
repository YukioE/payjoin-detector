"""
detect_neighbours — fetches prevout and outspend transactions for a given
txid, runs the standard heuristics on each, and prints all results.

Usage (async context):
    report = await detect_neighbours(detector, txid)
    report.print()
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import cast

from payjoin_detector.cli.printer import print_single_result
from payjoin_detector.core.detection import TxDetectionResult
from payjoin_detector.detector import Detector


@dataclass
class NeighbourResult:
    role: str  # e.g. "prevout:in[0]" or "outspend:out[1]"
    result: TxDetectionResult


@dataclass
class NeighboursReport:
    target_txid: str
    target_result: TxDetectionResult
    neighbour_results: list[NeighbourResult] = field(default_factory=list)

    def print(self) -> None:
        print("\n── target ──")
        print_single_result(self.target_result)

        if not self.neighbour_results:
            print("  (no neighbour transactions found)")
            return

        for nr in self.neighbour_results:
            print(f"── {nr.role} ──")
            print_single_result(nr.result)


async def detect_neighbours(
    detector: Detector,
    txid: str,
) -> NeighboursReport:
    """
    Run heuristics on *txid*, then fetch and analyse every prevout tx
    (backward) and every outspend tx (forward).

    Args:
        detector: A Detector whose provider supports get_outspend().
        txid:     Target transaction ID.

    Returns:
        A NeighboursReport ready to print().
    """
    target_result = await detector.detect(txid)
    tx = await detector.provider.get_transaction(txid)

    # --- collect neighbour (role, txid) pairs ----------------------------

    tasks: list[tuple[str, str]] = []

    # backward: one prevout tx per input
    for i, vin in enumerate(tx.inputs):
        if not vin.is_coinbase and vin.txid:
            tasks.append((f"prevout:in[{i}]", vin.txid))

    # forward: one outspend tx per spent output
    async def _safe_outspend(index: int) -> tuple[int, dict] | None:
        try:
            result = await detector.provider.get_outspend(txid, index)
            return (index, result) if result else None
        except Exception:
            return None

    outspends = cast(
        list[tuple[int, dict] | None],
        await asyncio.gather(*[_safe_outspend(i) for i in range(len(tx.outputs))]),
    )

    for entry in outspends:
        if entry is None:
            continue
        i, outspend = entry
        if outspend.get("spent") and outspend.get("txid"):
            tasks.append((f"outspend:out[{i}]", outspend["txid"]))

    # deduplicate (skip the target itself)
    seen: set[str] = {txid}
    unique: list[tuple[str, str]] = []
    for role, ntxid in tasks:
        if ntxid not in seen:
            seen.add(ntxid)
            unique.append((role, ntxid))

    # --- analyse each neighbour in parallel ------------------------------

    async def _analyse(role: str, ntxid: str) -> NeighbourResult:
        sub = Detector(provider=detector.provider, analyse_all=True)
        result = await sub.detect(ntxid)
        return NeighbourResult(role=role, result=result)

    neighbour_results: list[NeighbourResult] = list(
        await asyncio.gather(*[_analyse(r, t) for r, t in unique])
    )

    return NeighboursReport(
        target_txid=txid,
        target_result=target_result,
        neighbour_results=neighbour_results,
    )
