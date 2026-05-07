from payjoin_detector.core.transaction import Transaction
from payjoin_detector.core.heuristic import Heuristic, HeuristicResult


class NSequenceAsymmetryHeuristic(Heuristic):
    """
    NSA: checks if input nSequence values are asymmetric.

    - If inputs have different nSequence values, signal for PayJoin
    - If all inputs have same nSequence, neutral
    """

    name = "nSequence asymmetry heuristic"

    def check(self, tx: Transaction) -> HeuristicResult:
        if not tx.inputs:
            return HeuristicResult(
                name=self.name, score=0.0, signal="no inputs to analyze",
                html_signal="—"
            )

        seq_values = {input.sequence for input in tx.inputs}

        if len(seq_values) > 1:
            values_str = ", ".join(str(v) for v in sorted(seq_values))
            return HeuristicResult(
                name=self.name,
                score=2.0,
                signal=f"asymmetric nSequence values detected - {seq_values}",
                html_signal=f"{{{values_str}}}"
            )
        else:
            seq_value = seq_values.pop()
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal=f"all inputs have same nSequence - {seq_value}",
                html_signal=f"{{{seq_value}}}"
            )
