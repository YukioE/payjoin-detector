from payjoin_detector.transaction import Transaction
from payjoin_detector.heuristic import Heuristic, HeuristicResult


class NSequenceAsymmetryHeuristic(Heuristic):
    """
    NSA: checks if input nSequence values are asymmetric.

    - If inputs have different nSequence values, signal for PayJoin
    - If all inputs have same nSequence, neutral
    """

    name = "nSequence asymmetry heuristic"
    weight = 1.0

    def check(self, tx: Transaction) -> HeuristicResult:
        if not tx.inputs:
            return HeuristicResult(
                name=self.name, score=0.0, signal="no inputs to analyze"
            )

        seq_values = {input.sequence for input in tx.inputs}

        if len(seq_values) > 1:
            return HeuristicResult(
                name=self.name,
                score=0.5,
                signal=f"asymmetric nSequence values detected: {seq_values}",
            )
        else:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal=f"all inputs have same nSequence: {seq_values.pop()}",
            )
