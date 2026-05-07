"""
detect_neighbours — fetches prevout and outspend transactions for a given
txid, runs the standard heuristics on each, and prints all results.

report recurses one level into every depth-1 neighbour

Usage (async context):
    report = await detect_neighbours(detector, txid)
    report.print()
"""

from __future__ import annotations

import asyncio
import html
from dataclasses import dataclass, field

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
    nested_reports: list["NeighboursReport"] = field(default_factory=list)
    label: str = "target"

    def print(self) -> None:
        self._print_section()

    def to_html(self) -> str:
        """Generate an HTML report with one table per analysed neighbourhood."""
        sections = self._render_sections()
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
        .section {{ margin-top: 14px; }}
        .section h2 {{ margin: 0 0 8px 0; font-size: 12px; color: #333; }}
        .section .meta {{ margin-bottom: 8px; font-size: 11px; color: #555; }}
        .txid {{ display: block; max-width: 240px; word-break: break-all; white-space: normal; line-height: 1.2; color: #666; font-weight: 400; }}
        .status-note {{ margin: 8px 0 10px; padding: 8px; background: #fff4e5; border-left: 2px solid #f0ad4e; font-size: 11px; color: #5a4a2a; }}
        .status-note strong {{ display: block; margin-bottom: 2px; }}
        table {{ border-collapse: collapse; font-size: 11px; }}
        th {{ background: #f5f5f5; border: 1px solid #ddd; padding: 6px; text-align: center; font-weight: 600; min-width: 120px; vertical-align: top; }}
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
            <a href="https://mempool.space/tx/{html.escape(self.target_result.txid)}?mode=details" target="_blank">{html.escape(self.target_result.txid)}</a>
            ({len(self.neighbour_results)} depth-1 neighbour txs{f", {len(self.nested_reports)} depth-2 tables" if self.nested_reports else ""})
        </div>
        {sections}
    </div>
</body>
</html>"""

    def _extract_key_value(
        self, heur_name: str, signal: str, result: TxDetectionResult
    ) -> str:
        """Extract the most important value from heuristic result."""
        # Try to find the matching heuristic in the result object for html_signal
        for heur_result in result.heuristics_results or []:
            if heur_result.name == heur_name and heur_result.html_signal:
                return heur_result.html_signal

        # Fallback to signal parsing if html_signal not available
        import re

        msg = signal.split(": ", 1)[1] if ": " in signal else ""

        # Default: try to extract any numeric value
        match = re.search(r"[\d.]+", msg)
        return match.group(0) if match else "—"

    def _render_txid(self, txid: str) -> str:
        txid_html = html.escape(txid)
        return f"<span class='txid'>{txid_html}</span>"

    def _render_status_note(self, result: TxDetectionResult) -> str:
        if result.heuristics_results:
            return ""

        messages = [html.escape(line) for line in result.heuristics]
        if not messages:
            return ""

        title = messages[0]
        details = "<br>".join(messages[1:])
        return f"<div class='status-note'><strong>{title}</strong>{details}</div>"

    def _print_section(self, indent: int = 0) -> None:
        pad = " " * indent
        print(f"{pad}── {self.label} ──")
        print_single_result(self.target_result)

        if not self.neighbour_results:
            print(f"{pad}  (no neighbour transactions found)")
        else:
            for nr in self.neighbour_results:
                print(f"{pad}── {nr.role} ──")
                print_single_result(nr.result)

        for nested in self.nested_reports:
            print()
            nested._print_section(indent + 2)

    def _render_sections(self) -> str:
        sections = [self._render_section()]
        sections.extend(nested._render_sections() for nested in self.nested_reports)
        return "\n".join(sections)

    def _render_section(self) -> str:
        all_results = [(self.label, self.target_result)] + [
            (nr.role, nr.result) for nr in self.neighbour_results
        ]

        if not all_results:
            return "<div class='section'><div class='meta'>No transactions to display</div></div>"

        heuristic_names = self._ordered_heuristic_names(all_results)
        header_row = "<tr><th>Heuristic</th>"
        for role, result in all_results:
            header_row += (
                f"<th><div>{html.escape(role)}</div>"
                f"{self._render_txid(result.txid)}"
                f"<div style='font-size:10px'>{result.input_count}/{result.output_count} • {result.confidence * 100:.0f}%</div>"
                f"</th>"
            )
        header_row += "</tr>"

        data_rows = ""
        for heur_name in heuristic_names:
            data_rows += f"<tr><td>{heur_name}</td>"
            for _, result in all_results:
                heur_match = next(
                    (h for h in result.heuristics if heur_name in h), None
                )
                if heur_match:
                    color = (
                        "#28a745"
                        if heur_match.startswith("[+]")
                        else "#dc3545"
                        if heur_match.startswith("[-]")
                        else "#999"
                    )
                    key_value = self._extract_key_value(heur_name, heur_match, result)
                    data_rows += (
                        f"<td style='color:{color}'>{html.escape(key_value)}</td>"
                    )
                else:
                    data_rows += "<td style='color:#ccc'>—</td>"
            data_rows += "</tr>"

        return f"""
        <div class="section">
            <h2>{html.escape(self._section_title())}</h2>
            <div class="meta">
                <a href="https://mempool.space/tx/{self.target_result.txid}?mode=details" target="_blank">{html.escape(self.target_result.txid)}</a>
            </div>
            {self._render_status_note(self.target_result)}
            <table>
                {header_row}
                {data_rows}
            </table>
        </div>"""

    def _section_title(self) -> str:
        return (
            "Target transaction"
            if self.label == "target"
            else f"Neighbourhood for {self.label}"
        )

    def _ordered_heuristic_names(
        self, all_results: list[tuple[str, TxDetectionResult]]
    ) -> list[str]:
        all_heuristic_names: set[str] = set()
        for _, result in all_results:
            if not result.heuristics_results:
                continue
            for h in result.heuristics:
                name = h.split(": ")[0]
                name = (
                    name.replace("]", "")
                    .replace("[", "")
                    .replace("+", "")
                    .replace("-", "")
                    .strip()
                )
                if name:
                    all_heuristic_names.add(name)

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

        heuristic_names = [
            name for name in default_order if name in all_heuristic_names
        ]
        heuristic_names.extend(
            sorted(name for name in all_heuristic_names if name not in heuristic_names)
        )
        return heuristic_names


async def detect_neighbours(
    detector: Detector,
    txid: str,
    depth: int = 2,
    _visited: set[str] | None = None,
) -> NeighboursReport:
    """
    Run heuristics on *txid*, then fetch and analyse every prevout tx
    (backward) and every outspend tx (forward). When depth > 1, repeat the
    same analysis for each depth-1 neighbour and attach the nested reports.

    Args:
        detector: A Detector whose provider supports get_outspend().
        txid:     Target transaction ID.

    Returns:
        A NeighboursReport ready to print().
    """
    visited = set() if _visited is None else set(_visited)
    analysis_detector = Detector(provider=detector.provider, analyse_all=True)
    target_result = await analysis_detector.detect(txid)
    tx = await detector.provider.get_transaction(txid)

    neighbour_targets = await _collect_neighbour_targets(
        detector=detector,
        tx=tx,
        txid=txid,
        excluded_txids=visited | {txid},
    )

    async def _analyse(role: str, ntxid: str) -> NeighbourResult:
        result = await analysis_detector.detect(ntxid)
        return NeighbourResult(role=role, result=result)

    neighbour_results: list[NeighbourResult] = list(
        await asyncio.gather(*[_analyse(r, t) for r, t in neighbour_targets])
    )

    nested_reports: list[NeighboursReport] = []
    if depth > 1:
        for neighbour in neighbour_results:
            if neighbour.result.txid in visited:
                continue
            nested_reports.append(
                await detect_neighbours(
                    detector,
                    neighbour.result.txid,
                    depth=depth - 1,
                    _visited=visited | {txid},
                )
            )

    return NeighboursReport(
        target_txid=txid,
        target_result=target_result,
        neighbour_results=neighbour_results,
        nested_reports=nested_reports,
    )


async def _collect_neighbour_targets(
    detector: Detector,
    tx,
    txid: str,
    excluded_txids: set[str],
) -> list[tuple[str, str]]:
    tasks: list[tuple[str, str]] = []

    for i, vin in enumerate(tx.inputs):
        if not vin.is_coinbase and vin.txid and vin.txid not in excluded_txids:
            tasks.append((f"prevout:in[{i}]", vin.txid))

    async def _safe_outspend(index: int) -> tuple[int, dict] | None:
        try:
            result = await detector.provider.get_outspend(txid, index)
            return (index, result) if result else None
        except Exception:
            return None

    outspends = await asyncio.gather(
        *[_safe_outspend(i) for i in range(len(tx.outputs))]
    )

    for entry in outspends:
        if entry is None:
            continue
        i, outspend = entry
        if (
            outspend.get("spent")
            and outspend.get("txid")
            and outspend["txid"] not in excluded_txids
        ):
            tasks.append((f"outspend:out[{i}]", outspend["txid"]))

    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for role, ntxid in tasks:
        if ntxid not in seen:
            seen.add(ntxid)
            unique.append((role, ntxid))
    return unique
