from payjoin_detector.core.transaction import Transaction
from payjoin_detector.core.heuristic import Heuristic, HeuristicResult


class SignatureAsymmetryHeuristic(Heuristic):
    """
    SAH: Detects asymmetric ECDSA signatures across inputs.

    - Only signals when all inputs are the same type
    - If some signatures are high-R and some low-R, positive score
    - If inputs are mixed types, neutral
    """

    name = "Signature asymmetry heuristic"

    def check(self, tx: Transaction) -> HeuristicResult:
        # Gather input types
        input_types = {
            inp.prevout.scriptpubkey_type for inp in tx.inputs if inp.prevout
        }

        # If input types are not uniform, signature asymmetry is expected; return neutral
        if len(input_types) > 1:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal=f"mixed input types ({input_types}) - asymmetry expected",
                html_signal="—"
            )

        # Check signature R-types (limit to first 10 signatures)
        input_r_types = {}
        r_types = set()
        sig_count = 0
        max_sigs = 10

        for idx, inp in enumerate(tx.inputs):
            if not inp.witness:
                continue

            for item in inp.witness:
                if sig_count >= max_sigs:
                    break

                sig_bytes = bytes.fromhex(item) if isinstance(item, str) else item

                if len(sig_bytes) < 3:
                    continue

                # Remove sighash byte
                sig_der = sig_bytes[:-1]

                if len(sig_der) < 4 or sig_der[0] != 0x30:
                    continue

                try:
                    r_len = sig_der[3]
                    r_value = sig_der[4 : 4 + r_len]

                    if not r_value:
                        continue

                    high_r = r_value[0] == 0x00
                    r_type = "high-R" if high_r else "low-R"

                    input_r_types[idx] = r_type
                    r_types.add(r_type)
                    sig_count += 1

                    break

                except Exception:
                    continue

            if sig_count >= max_sigs:
                break

        if len(r_types) > 1:
            types_str = ", ".join(sorted(r_types))
            return HeuristicResult(
                name=self.name,
                score=2.0,
                signal=f"signature asymmetry detected - {input_r_types}",
                html_signal=f"{{{types_str}}}"
            )
        else:
            if input_r_types:
                r_type = list(r_types)[0] if r_types else "unknown"
                return HeuristicResult(
                    name=self.name,
                    score=0.0,
                    signal=f"all signatures consistent - {input_r_types}",
                    html_signal=f"{{{r_type}}}"
                )
            else:
                return HeuristicResult(
                    name=self.name,
                    score=0.0,
                    signal="no signature data",
                    html_signal="—"
                )
