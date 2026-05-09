from collections import Counter
from payjoin_detector.core.transaction import Transaction
from payjoin_detector.core.heuristic import Heuristic, HeuristicResult


class CoinJoinHeuristic(Heuristic):
    """
    CJH: detects if a transaction follows a CoinJoin pattern using mempool.space's heuristic.
    Conditions (all must be true):
      - At least 5 inputs and 5 outputs
      - No address reuse between inputs and outputs
      - Unique input value count + unique output value count <= (total inputs + total outputs) / 2
    """

    name = "CoinJoin pattern heuristic"

    def check(self, tx: Transaction) -> HeuristicResult:
        inputs = tx.inputs
        outputs = tx.outputs

        # Condition 1: at least 5 inputs and 5 outputs
        if len(inputs) < 5 or len(outputs) < 5:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="not enough inputs/outputs to be CoinJoin (need >=5 each)",
                html_signal="Too few inputs/outputs",
            )

        # Condition 2: no address reuse between inputs and outputs
        input_addresses = Counter(
            i.prevout.scriptpubkey_address for i in inputs if i.prevout
        )
        output_addresses = Counter(
            o.scriptpubkey_address for o in outputs if o.scriptpubkey_address
        )

        reuse_score = (
            max(
                (input_addresses[addr] + output_addresses[addr])
                for addr in output_addresses
            )
            if output_addresses
            else 0
        )

        if reuse_score > 1:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="address reuse detected - not a CoinJoin pattern",
                html_signal="Address reuse",
            )

        # Condition 3: unique value diversity check
        # (unique input values + unique output values) <= (total inputs + total outputs) / 2
        unique_in_values = len(set(i.prevout.value for i in inputs if i.prevout))
        unique_out_values = len(set(o.value for o in outputs))
        total_txos = len(inputs) + len(outputs)

        if (unique_in_values + unique_out_values) <= total_txos / 2:
            return HeuristicResult(
                name=self.name,
                score=-3.0,
                signal=(
                    f"CoinJoin pattern detected - {len(inputs)} inputs, {len(outputs)} outputs"
                ),
                html_signal="Possible CoinJoin",
            )

        return HeuristicResult(
            name=self.name,
            score=0.0,
            signal="no CoinJoin pattern detected",
            html_signal="Not CoinJoin",
        )
