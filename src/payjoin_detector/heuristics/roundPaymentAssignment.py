from payjoin_detector.core.transaction import Transaction
from payjoin_detector.core.heuristic import Heuristic, HeuristicResult


class RoundPaymentAssignmentHeuristic(Heuristic):
    """
    RPAH: Detects round payments between inputs and outputs,
    which is common in PayJoin transactions where:
    - Payment amount is a round number
    - Receiver contributes a small input relative to sender's change
    """

    name = "Round payment assignment heuristic"

    def check(self, tx: Transaction) -> HeuristicResult:
        if len(tx.inputs) != 2 or len(tx.outputs) != 2:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="TX does not have exactly 2 inputs and 2 outputs",
                html_signal="Wrong structure"
            )

        inputs: list[int] = [inp.prevout.value for inp in tx.inputs if inp.prevout]
        outputs: list[int] = [out.value for out in tx.outputs]

        if not inputs or not outputs:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="No inputs or outputs to analyze",
                html_signal="—"
            )

        round_matches = []

        for i_val in inputs:
            for o_val in outputs:
                payment = abs(o_val - i_val)
                if payment % 100 == 0 and payment != 0:
                    round_matches.append((i_val, o_val, payment))
                    if len(round_matches) >= 5:
                        break
            if len(round_matches) >= 5:
                break

        if round_matches:
            payment = round_matches[0][2]
            return HeuristicResult(
                name=self.name,
                score=1.0,
                signal=f"Round payment detected - {round_matches}",
                html_signal=f"payment found ({payment} sats)"
            )

        return HeuristicResult(
            name=self.name,
            score=0.0,
            signal="no round payment detected",
            html_signal="No round payment"
        )
