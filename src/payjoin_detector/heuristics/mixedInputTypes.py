from datetime import datetime
from payjoin_detector.core.transaction import Transaction
from payjoin_detector.core.heuristic import Heuristic, HeuristicResult

SEPT_2024 = int(datetime(2024, 9, 1).timestamp())


class MixedInputTypesHeuristic(Heuristic):
    """
    MITH: checks whether all inputs are of the same script type.

    - Mixed inputs before 09-2024 are a strong signal against payjoin (-1)
    - Mixed inputs after 09-2024 are a weak signal for payjoin
    - Uniform inputs give neutral score (0)
    """

    name = "Mixed input types heuristic"

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
                html_signal="—",
            )

        tx_time = tx.status.block_time

        if len(input_types) > 1:
            if tx_time and tx_time < SEPT_2024:
                types_list = ", ".join(sorted(input_types))
                return HeuristicResult(
                    name=self.name,
                    score=-3.0,
                    signal=f"mixed input types before Sep 2024 - {input_types}",
                    html_signal=f"mixed types (pre 09-2024)",
                )
            else:
                types_list = ", ".join(sorted(input_types))
                return HeuristicResult(
                    name=self.name,
                    score=0.0,
                    signal=f"mixed input types - {input_types}",
                    html_signal=f"{{{types_list}}}",
                )

        input_type = input_types.pop()
        return HeuristicResult(
            name=self.name,
            score=0.4,
            signal=f"all inputs same type - {input_type}",
            html_signal=f"{{{input_type}}}",
        )
