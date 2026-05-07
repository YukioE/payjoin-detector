from payjoin_detector.core.heuristic import Heuristic, HeuristicResult
from payjoin_detector.core.transaction import Transaction


class AddressReuseHeuristic(Heuristic):
    """
    ARH: Detects if any input address appears in the outputs.

    - Usually, wallets don’t reuse addresses for change.
    - If a user explicitly reuses one of their addresses, it is probably not a PayJoin implementation.
    """

    name = "Address reuse heuristic"

    def check(self, tx: Transaction) -> HeuristicResult:
        input_addresses = {
            inp.prevout.scriptpubkey_address
            for inp in tx.inputs
            if inp.prevout is not None and inp.prevout.scriptpubkey_address is not None
        }

        output_addresses = {
            out.scriptpubkey_address
            for out in tx.outputs
            if out.scriptpubkey_address is not None
        }

        reused = input_addresses & output_addresses

        if reused:
            if len(reused) == 1:
                return HeuristicResult(
                    name=self.name,
                    score=-1.0,
                    signal=f"input address(es) reappear in outputs: {reused}",
                    html_signal="address reused"
                )
            else:
                return HeuristicResult(
                    name=self.name,
                    score=-1.0,
                    signal=f"input address(es) reappear in outputs: {reused}",
                    html_signal=f"{len(reused)} addresses reused"
                )
        else:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="no address reuse detected",
                html_signal="no reuse"
            )
