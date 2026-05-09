from payjoin_detector.core.transaction import Transaction, TxInput
from payjoin_detector.core.heuristic import Heuristic, HeuristicResult


def get_input_script_type(inp: TxInput) -> str:
    """Infer script type from prevout or witness/scriptsig fields."""
    if inp.prevout:
        return inp.prevout.scriptpubkey_type
    if inp.witness:
        return "v0_p2wpkh"
    if inp.scriptsig:
        return "p2pkh"
    return "unknown"


def estimate_input_weight(inp: TxInput) -> int:
    """
    Estimate input weight in weight units (WU).
    Based on the transaction size calculator field sizes,
    converted to weight: non-witness bytes * 4, witness bytes * 1.
    """
    script_type = get_input_script_type(inp)

    # Outpoint (txid 32 + vout 4) = 36 bytes, nSequence = 4 bytes → always non-witness
    base_bytes = 36 + 4  # outpoint + nsequence

    if script_type in ("v0_p2wpkh", "p2wpkh"):
        # scriptSig is empty (1 byte length field, 0 bytes content)
        base_bytes += 1
        # Witness: size(72) sig + size(33) pubkey = 73 + 34 = 107 witness bytes
        # Plus 1 byte witness item count
        witness_bytes = 1 + 73 + 34  # = 108
        return base_bytes * 4 + witness_bytes

    elif script_type in ("v0_p2wsh", "p2wsh"):
        # scriptSig empty
        base_bytes += 1
        # Witness 2-of-3: 1 + 1 + 73 + 73 + 106 = 254 witness bytes
        witness_bytes = 1 + 1 + 73 + 73 + 106  # = 254
        return base_bytes * 4 + witness_bytes

    elif script_type == "p2pkh":
        # scriptSig: 1 (length) + 107 (OP_PUSH72 sig OP_PUSH33 pubkey) = 108 bytes
        base_bytes += 1 + 107
        return base_bytes * 4

    elif script_type in ("p2sh", "p2sh-p2wpkh", "p2sh-p2wsh"):
        # P2SH 2-of-3: 3 (length varint) + 254 (redeem script + sigs) = 257 bytes
        base_bytes += 3 + 254
        return base_bytes * 4

    elif script_type in ("v1_p2tr", "p2tr"):
        # scriptSig empty
        base_bytes += 1
        # Witness: 1 (item count) + 65 (size(64) schnorr_sig) = 66 witness bytes
        witness_bytes = 1 + 65
        return base_bytes * 4 + witness_bytes

    else:
        # Unknown: fall back to p2pkh estimate
        base_bytes += 1 + 107
        return base_bytes * 4


def estimate_output_weight(scriptpubkey_type: str) -> int:
    """
    Estimate output weight in WU.
    Output fields are all non-witness: nValue (8) + spk_length (1) + spk (varies).
    """
    spk_sizes = {
        "p2pkh": 25,
        "p2wpkh": 22,
        "v0_p2wpkh": 22,
        "p2sh": 23,
        "p2wsh": 34,
        "v0_p2wsh": 34,
        "p2tr": 34,
        "v1_p2tr": 34,
    }
    spk = spk_sizes.get(scriptpubkey_type, 25)  # default p2pkh
    return (8 + 1 + spk) * 4


def estimate_tx_weight(tx: Transaction) -> int:
    """
    Estimate total transaction weight in WU.
    Overhead: nVersion(4) + input_count(1) + output_count(1) + nLockTime(4) = 10 bytes non-witness.
    If segwit inputs present, add marker+flag = 2 witness bytes.
    """
    has_segwit = any(
        get_input_script_type(i)
        in ("v0_p2wpkh", "p2wpkh", "v0_p2wsh", "p2wsh", "v1_p2tr", "p2tr")
        for i in tx.inputs
    )

    overhead_bytes = 4 + 1 + 1 + 4  # nVersion + input_count + output_count + nLockTime
    overhead_wu = overhead_bytes * 4
    if has_segwit:
        overhead_wu += 2  # segwit marker + flag (witness bytes)

    input_wu = sum(estimate_input_weight(i) for i in tx.inputs)
    output_wu = sum(estimate_output_weight(o.scriptpubkey_type) for o in tx.outputs)

    return overhead_wu + input_wu + output_wu


def fee_rate_from_weight(fee_sats: int, weight_wu: int) -> float:
    """Convert fee + weight to sat/vbyte. vbytes = ceil(weight / 4)."""
    vbytes = weight_wu / 4
    return fee_sats / vbytes if vbytes > 0 else 0.0


def is_round_fee_rate(fee_rate: float, tolerance: float = 0.05) -> bool:
    """
    A fee rate is 'round' if it is within `tolerance` of a whole number.
    e.g. 2.0 sat/vb, 5.0 sat/vb, 10.0 sat/vb etc.
    """
    return abs(fee_rate - round(fee_rate)) <= tolerance


def estimate_tx_weight_without_input(tx: Transaction, exclude_idx: int) -> int:
    """
    Estimate transaction weight with one input removed.
    Re-evaluates segwit flag based on remaining inputs.
    """
    remaining_inputs = [i for idx, i in enumerate(tx.inputs) if idx != exclude_idx]

    has_segwit = any(
        get_input_script_type(i)
        in ("v0_p2wpkh", "p2wpkh", "v0_p2wsh", "p2wsh", "v1_p2tr", "p2tr")
        for i in remaining_inputs
    )

    overhead_bytes = 4 + 1 + 1 + 4
    overhead_wu = overhead_bytes * 4
    if has_segwit:
        overhead_wu += 2

    input_wu = sum(estimate_input_weight(i) for i in remaining_inputs)
    output_wu = sum(estimate_output_weight(o.scriptpubkey_type) for o in tx.outputs)

    return overhead_wu + input_wu + output_wu


class RoundFeeHeuristic(Heuristic):
    """
    RFH: detects whether the fee rate is suspiciously non-round in a way
    consistent with a PayJoin transaction.

    - see https://github.com/bitcoin/bips/blob/master/bip-0078.mediawiki#defeating-heuristics-based-on-the-fee-calculation
    """

    name = "Round fee heuristic"

    def check(self, tx: Transaction) -> HeuristicResult:
        if not tx.inputs or tx.fee is None:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="insufficient data to evaluate fee rate",
                html_signal="—",
            )

        actual_weight = tx.weight if tx.weight else estimate_tx_weight(tx)
        actual_fee_rate = fee_rate_from_weight(tx.fee, actual_weight)

        if is_round_fee_rate(actual_fee_rate):
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal=(f"fee rate {actual_fee_rate:.2f} sat/vb is round"),
                html_signal=f"Round: {actual_fee_rate:.1f} sat/vB",
            )

        # Non-round fee rate: run the input removal test
        suspicious_inputs = []
        for idx in range(len(tx.inputs)):
            reduced_weight = estimate_tx_weight_without_input(tx, exclude_idx=idx)
            if reduced_weight <= 0:
                continue
            reduced_fee_rate = fee_rate_from_weight(tx.fee, reduced_weight)
            if is_round_fee_rate(reduced_fee_rate):
                suspicious_inputs.append((idx, reduced_fee_rate))

        if suspicious_inputs:
            details = ", ".join(
                f"input[{i}] → {r:.2f} sat/vb" for i, r in suspicious_inputs
            )
            return HeuristicResult(
                name=self.name,
                score=1.0,
                signal=(
                    f"fee rate {actual_fee_rate:.2f} sat/vb is non-round; removing input(s) restores a round rate: {details}"
                ),
                html_signal=f"Non-round: {actual_fee_rate:.1f} → {suspicious_inputs[0][1]:.1f}",
            )

        return HeuristicResult(
            name=self.name,
            score=-0.25,
            signal=(f"fee rate {actual_fee_rate:.2f} sat/vb is non-round"),
            html_signal=f"Non-round: {actual_fee_rate:.1f} sat/vB",
        )
