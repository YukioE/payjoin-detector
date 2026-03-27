from payjoin_detector.core.transaction import Transaction
from payjoin_detector.core.heuristic import Heuristic, HeuristicResult


class SignatureAsymmetryHeuristic(Heuristic):
    """
    SAH: Detects asymmetric ECDSA signatures across inputs.

    - If some signatures are low-R and some are high-R, signal for PayJoin
    - If all signatures have the same R-type, neutral
    """

    name = "Signature asymmetry heuristic"
    weight = 1.0

    def check(self, tx: Transaction) -> HeuristicResult:
        r_types = set()

        for inp in tx.inputs:
            if not inp.witness or len(inp.witness) < 1:
                continue

            sig_bytes = (
                bytes.fromhex(inp.witness[0])
                if isinstance(inp.witness[0], str)
                else inp.witness[0]
            )

            if len(sig_bytes) < 3:
                continue

            # DER-encoded signature: first byte 0x30, second = length, then r & s
            # R starts at byte 3 (DER header = 0x30 len, 0x02 len_r)
            r_len = sig_bytes[3]
            r_value = sig_bytes[4 : 4 + r_len]

            # Check if R needs leading zero pad (high-R) or not (low-R)
            high_r = r_value[0] == 0x00
            r_types.add("high" if high_r else "low")

        if len(r_types) > 1:
            return HeuristicResult(
                name=self.name,
                score=0.8,
                signal=f"signature asymmetry detected - {r_types}",
            )
        else:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal=f"all signatures consistent - {r_types.pop()}"
                if r_types
                else "no signature data",
            )
