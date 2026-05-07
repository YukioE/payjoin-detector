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

        if input_count <= 3 and output_count == 2:
            return HeuristicResult(
                name=self.name, score=1.0, signal=f"I/O count is {input_count}/2",
                html_signal="small"
            )
        elif input_count <= 5 and output_count <= 3:
            return HeuristicResult(
                name=self.name, score=0.5, signal=f"I/O count is {input_count}/{output_count}",
                html_signal="small"
            )
        else:
            return HeuristicResult(
                name=self.name, score=0.0, signal="I/O counts not small",
                html_signal="large"
            )
