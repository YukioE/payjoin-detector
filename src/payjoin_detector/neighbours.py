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

    def to_html(self) -> str:
        """Generate a compact side-by-side HTML report showing only key values."""
        all_results = [(None, self.target_result)] + [
            (nr.role, nr.result) for nr in self.neighbour_results
        ]

        if not all_results:
            return "<html><body>No transactions to display</body></html>"

        # Collect all unique heuristic names (deduplicate)
        all_heuristic_names = set()
        for _, result in all_results:
            for h in result.heuristics:
                # Extract name between status brackets and colon
                # Remove prefix like [+], [-], [ ], or ] if present
                name = h.split(": ")[0]  # Get part before colon
                # Remove all brackets and common prefixes
                name = (
                    name.replace("]", "")
                    .replace("[", "")
                    .replace("+", "")
                    .replace("-", "")
                    .strip()
                )
                if name:  # Only add non-empty names
                    all_heuristic_names.add(name)

        # Define the order of heuristics as in DEFAULT_HEURISTICS
        default_order = [
            "Unnecessary input heuristic",
            "Small I/O counts heuristic",
            "Mixed input types heuristic",
            "Mixed output types heuristic",
            "Address reuse heuristic",
            "Round fee heuristic",
            "Round output heuristic",
            "Round payment assignment heuristic",
            "CoinJoin pattern heuristic",
            "Input value disparity heuristic",
            "nSequence asymmetry heuristic",
            "Signature asymmetry heuristic",
        ]
        
        # Sort heuristic names following default order, then add any extras
        heuristic_names = []
        for default_name in default_order:
            if default_name in all_heuristic_names:
                heuristic_names.append(default_name)
        
        # Add any remaining heuristics not in default (like Clustering)
        for name in sorted(all_heuristic_names):
            if name not in heuristic_names:
                heuristic_names.append(name)

        # Build table rows
        header_row = "<tr><th>Heuristic</th>"
        for role, result in all_results:
            label = role if role else "TARGET"
            txid_short = result.txid[:8]
            header_row += f"<th><div>{label}</div><div style='font-size:9px; color:#666'>{txid_short}...</div><div style='font-size:10px'>{result.input_count}/{result.output_count} • {result.confidence * 100:.0f}%</div></th>"
        header_row += "</tr>"

        # Build heuristic rows
        data_rows = ""
        for heur_name in heuristic_names:
            data_rows += f"<tr><td>{heur_name}</td>"
            for role, result in all_results:
                heur_match = None
                for h in result.heuristics:
                    if heur_name in h:
                        heur_match = h
                        break

                if heur_match:
                    status = (
                        "[+]"
                        if heur_match.startswith("[+]")
                        else "[-]"
                        if heur_match.startswith("[-]")
                        else "[ ]"
                    )
                    color = (
                        "#28a745"
                        if heur_match.startswith("[+]")
                        else "#dc3545"
                        if heur_match.startswith("[-]")
                        else "#999"
                    )

                    # Extract html_signal from result if available
                    key_value = self._extract_key_value(heur_name, heur_match, result)

                    data_rows += f"<td style='color:{color}'>{key_value}</td>"
                else:
                    data_rows += f"<td style='color:#ccc'>—</td>"
            data_rows += "</tr>"

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PayJoin Neighbours Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 10px; background: #f5f5f5; }}
        .container {{ background: white; border-radius: 4px; padding: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow-x: auto; }}
        h1 {{ margin: 0 0 10px 0; font-size: 14px; color: #333; }}
        .info {{ margin-bottom: 12px; padding: 8px; background: #f0f7ff; border-left: 2px solid #0066cc; font-size: 11px; }}
        table {{ border-collapse: collapse; font-size: 11px; }}
        th {{ background: #f5f5f5; border: 1px solid #ddd; padding: 6px; text-align: center; font-weight: 600; min-width: 90px; }}
        th:first-child {{ text-align: left; min-width: 130px; }}
        td {{ border: 1px solid #ddd; padding: 5px 6px; text-align: center; }}
        td:first-child {{ text-align: left; font-weight: 500; background: #fafafa; }}
        tr:nth-child(even) td {{ background: #fafafa; }}
        tr:nth-child(even) td:first-child {{ background: #f5f5f5; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>PayJoin Neighbours Analysis</h1>
        <div class="info">
            <a href="https://mempool.space/tx/{self.target_result.txid}?mode=details" target="_blank">{self.target_result.txid}</a>
            ({len(self.neighbour_results)} neighbour txs)
        </div>
        <table>
            {header_row}
            {data_rows}
        </table>
    </div>
</body>
</html>"""

    def _extract_key_value(self, heur_name: str, signal: str, result: TxDetectionResult) -> str:
        """Extract the most important value from heuristic result."""
        # Try to find the matching heuristic in the result object for html_signal
        for heur_result in result.heuristics_results:
            if heur_result.name == heur_name and heur_result.html_signal:
                return heur_result.html_signal
        
        # Fallback to signal parsing if html_signal not available
        import re
        msg = signal.split(": ", 1)[1] if ": " in signal else ""
        
        # Default: try to extract any numeric value
        match = re.search(r"[\d.]+", msg)
        return match.group(0) if match else "—"


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
