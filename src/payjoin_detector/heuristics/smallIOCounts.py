from payjoin_detector.core.heuristic import Heuristic, HeuristicResult
from payjoin_detector.core.transaction import Transaction


class SmallIOCountsHeuristic(Heuristic):
    """
    SIOCH: Detects small counts of inputs & outputs

    - threshold is <=5 Inputs and <=3 Outputs
    """

    name = "Small I/O counts heuristic"

    def check(self, tx: Transaction) -> HeuristicResult:
        input_count = len(tx.inputs)
        output_count = len(tx.outputs)

        if input_count <= 5 and output_count <= 3:
            return HeuristicResult(
                name=self.name, score=0.5, signal="small I/O counts detected"
            )
        else:
            return HeuristicResult(
                name=self.name, score=0.0, signal="I/O counts not small"
            )
