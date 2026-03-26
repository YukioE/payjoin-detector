from datetime import datetime
from payjoin_detector.transaction import Transaction
from payjoin_detector.heuristic import Heuristic, HeuristicResult

SEPT_2024 = int(datetime(2024, 9, 1).timestamp())


class MixedInputTypesHeuristic(Heuristic):
    """
    ITCH: checks whether all inputs are of the same script type.

    - Mixed inputs before 09-2024 are a strong signal against payjoin
    - Mixed inputs after 09-2024 are a weak signal for payjoin
    - Uniform inputs give neutral score
    """

    name = "Mixed input types heuristic"
    weight = 1.0

    def check(self, tx: Transaction) -> HeuristicResult:
        input_types = {
            inp.prevout.scriptpubkey_type
            for inp in tx.inputs
            if inp.prevout is not None
        }

        if not input_types:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="no prevout data to determine input types",
            )

        tx_time = tx.status.block_time

        if len(input_types) > 1:
            if tx_time and tx_time < SEPT_2024:
                return HeuristicResult(
                    name=self.name,
                    score=-1.0,
                    signal=f"mixed input types before Sep 2024 - {input_types}",
                )
            else:
                return HeuristicResult(
                    name=self.name,
                    score=0.3,
                    signal=f"mixed input types - {input_types}",
                )

        return HeuristicResult(
            name=self.name,
            score=0.0,
            signal=f"all inputs same type - {input_types.pop()}",
        )
