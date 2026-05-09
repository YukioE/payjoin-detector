from payjoin_detector.core.heuristic import Heuristic, HeuristicResult
from payjoin_detector.core.transaction import Transaction


class InputValueDisparityHeuristic(Heuristic):
    """
    IVDH: Detects a large delta between input values

    - large delta is a small signal for payjoin
    """

    name = "Input value disparity heuristic"

    def check(self, tx: Transaction) -> HeuristicResult:
        values = [inp.prevout.value for inp in tx.inputs if inp.prevout is not None]

        if not values:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="no input values to analyze",
                html_signal="—",
            )

        min_value = min(values)
        max_value = max(values)

        ratio = min_value / max_value if max_value > 0 else float("inf")

        if ratio < 0.3:
            return HeuristicResult(
                name=self.name,
                score=0.3,
                signal="large delta between min and max input values detected",
                html_signal="—",
            )
        else:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="no large disparity between min and max input values detected",
                html_signal="—",
            )
