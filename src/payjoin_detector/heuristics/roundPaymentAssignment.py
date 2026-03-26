from payjoin_detector.transaction import Transaction
from payjoin_detector.heuristic import Heuristic, HeuristicResult


class RoundPaymentAssignmentHeuristic(Heuristic):
    """
    RPAH: Detects round payments between inputs and outputs,
    which is common in PayJoin transactions where:
    - Payment amount is a round number
    - Receiver contributes a small input relative to sender's change
    """

    name = "Round payment assignment heuristic"
    weight = 1.0

    def check(self, tx: Transaction) -> HeuristicResult:
        inputs: list[int] = [inp.prevout.value for inp in tx.inputs if inp.prevout]
        outputs: list[int] = [out.value for out in tx.outputs]

        if not inputs or not outputs:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="No inputs or outputs to analyze",
            )

        round_matches = []

        for i_val in inputs:
            for o_val in outputs:
                payment = abs(o_val - i_val)
                if payment % 100 == 0 and payment != 0:
                    round_matches.append((i_val, o_val, payment))

        if round_matches:
            return HeuristicResult(
                name=self.name,
                score=0.8,
                signal=f"Round payment detected - {round_matches}",
            )

        return HeuristicResult(
            name=self.name,
            score=0.0,
            signal="no round payment detected",
        )
