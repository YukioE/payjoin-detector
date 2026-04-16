from payjoin_detector.core.transaction import Transaction
from payjoin_detector.core.heuristic import Heuristic, HeuristicResult


class MixedOutputTypesHeuristic(Heuristic):
    """
    MOTH: checks whether all outputs are of the same script type.

    - Mixed outputs give a neutral score
    - Uniform outputs give a slight positive score
    """

    name = "Mixed output types heuristic"

    def check(self, tx: Transaction) -> HeuristicResult:
        output_types = {out.scriptpubkey_type for out in tx.outputs if out is not None}

        if not output_types:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="no prevout data to determine input types",
            )

        if len(output_types) > 1:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal=f"mixed output types - {output_types}",
            )

        return HeuristicResult(
            name=self.name,
            score=0.3,
            signal=f"all outputs same type - {output_types.pop()}",
        )
