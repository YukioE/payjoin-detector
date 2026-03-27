from payjoin_detector.core.transaction import Transaction
from payjoin_detector.core.heuristic import Heuristic, HeuristicResult


class CoinJoinHeuristic(Heuristic):
    """
    CJH: detects if a transaction follows a typical CoinJoin pattern.

    - If CoinJoin pattern detected, signal against PayJoin
    - If not, neutral
    """

    name = "CoinJoin pattern heuristic"
    weight = 1.0

    def check(self, tx: Transaction) -> HeuristicResult:
        outputs = [o.value for o in tx.outputs]

        if not outputs or len(outputs) < 2:
            return HeuristicResult(
                name=self.name, score=0.0, signal="not enough outputs to be CoinJoin"
            )

        from collections import Counter

        output_counts = Counter(outputs)
        common_outputs = [v for v, count in output_counts.items() if count >= 3]

        if common_outputs:
            return HeuristicResult(
                name=self.name,
                score=-1.0,
                signal=f"CoinJoin pattern detected - {len(common_outputs)} values repeated >=3 times",
            )

        return HeuristicResult(
            name=self.name, score=0.0, signal="no CoinJoin pattern detected"
        )
