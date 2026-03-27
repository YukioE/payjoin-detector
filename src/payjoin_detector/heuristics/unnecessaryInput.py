from payjoin_detector.core.transaction import Transaction
from payjoin_detector.core.heuristic import Heuristic, HeuristicResult


class UnnecessaryInputHeuristic(Heuristic):
    """
    UIH2: if the smallest output is larger than the smallest input,
    there was no need for that extra input under a normal payment workflow.
    This suggests a second party added inputs (payjoin).

    Score: 0.8 if triggered, else 0.0
    """

    name = "Unnecessary input heuristic"
    weight = 1.2

    def check(self, tx: Transaction) -> HeuristicResult:
        input_values = []
        for i in tx.inputs:
            if i.prevout is None:
                return HeuristicResult(
                    name=self.name, score=0.0, signal="missing prevout data"
                )
            input_values.append(i.prevout.value)

        output_values = [o.value for o in tx.outputs]

        if not input_values or not output_values:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="either input or output values missing",
            )

        min_input = min(input_values)
        min_output = min(output_values)

        if min_output > min_input:
            return HeuristicResult(
                name=self.name,
                score=0.8,
                signal=f"UIH2 smallest output ({min_output} sat) > smallest input ({min_input} sat)",
            )
        return HeuristicResult(
            name=self.name,
            score=0.0,
            signal=f"UIH1 optimal change detected, smallest output ({min_output} sat) < smallest input ({min_input} sat)",
        )
