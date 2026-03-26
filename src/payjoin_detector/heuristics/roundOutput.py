from payjoin_detector.transaction import Transaction
from payjoin_detector.heuristic import Heuristic, HeuristicResult


class RoundOutputHeuristic(Heuristic):
    """
    ROH: checks whether outputs are 'round' numbers.

    - If all outputs are round numbers (e.g., multiples of 1000 sats), unlikely to be PayJoin
    - If all outputs are non-round, small signal for PayJoin
    - If outputs are mixed round and non-round, small signal against PayJoin
    """

    name = "Round output heuristic"
    weight = 1.0

    def check(self, tx: Transaction) -> HeuristicResult:
        if not tx.outputs:
            return HeuristicResult(
                name=self.name, score=0.0, signal="no outputs to analyze"
            )

        round_threshold = 1000
        is_round = [o.value % round_threshold == 0 for o in tx.outputs]

        if all(is_round):
            return HeuristicResult(
                name=self.name,
                score=-0.5,
                signal=f"all outputs are round multiples of {round_threshold} sats, unlikely PayJoin",
            )
        elif all(not r for r in is_round):
            return HeuristicResult(
                name=self.name,
                score=0.2,
                signal="all outputs non-round",
            )
        else:
            return HeuristicResult(
                name=self.name,
                score=-0.2,
                signal="mixed round and non-round outputs",
            )
