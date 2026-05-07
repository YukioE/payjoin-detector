from payjoin_detector.core.transaction import Transaction
from payjoin_detector.core.heuristic import Heuristic, HeuristicResult


class RoundOutputHeuristic(Heuristic):
    """
    ROH: checks whether outputs are 'round' numbers.

    - If all outputs are round numbers (e.g., multiples of 1000 sats), unlikely to be PayJoin
    - If all outputs are non-round, small signal for PayJoin
    - If outputs are mixed round and non-round, small signal against PayJoin
    """

    name = "Round output heuristic"

    def check(self, tx: Transaction) -> HeuristicResult:
        if not tx.outputs:
            return HeuristicResult(
                name=self.name, score=0.0, signal="no outputs to analyze",
                html_signal="—"
            )

        round_threshold = 100
        is_round = [o.value % round_threshold == 0 for o in tx.outputs]

        if all(is_round):
            return HeuristicResult(
                name=self.name,
                score=-1.0,
                signal=f"all outputs are round multiples of {round_threshold} sats, unlikely PayJoin",
                html_signal="All round"
            )
        elif all(not r for r in is_round):
            return HeuristicResult(
                name=self.name,
                score=0.2,
                signal="all outputs non-round",
                html_signal="All non-round"
            )
        else:
            return HeuristicResult(
                name=self.name,
                score=-0.5,
                signal="mixed round and non-round outputs",
                html_signal="Mixed (round/non-round)"
            )
