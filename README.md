# Python PayJoin Detector

A lightweight tool to detect potential PayJoin transactions using heuristic analysis.

## Repository overview

The project is a Python CLI app (`payjoin-detector`) that fetches Bitcoin transaction data from a provider and runs a set of heuristics to calculate a PayJoin confidence score.

- `src/payjoin_detector/main.py` - CLI entrypoint and command dispatch (`transaction`, `block`, `neighbours`)
- `src/payjoin_detector/cli/` - argument parsing, command handlers, output/debug formatting
- `src/payjoin_detector/detector.py` - core detection pipeline and heuristic orchestration
- `src/payjoin_detector/heuristics/` - individual heuristic implementations (one file per heuristic)
- `src/payjoin_detector/providers/` - data source adapters (currently electrs and Bitcoin Core)
- `src/payjoin_detector/core/` - shared domain models and interfaces (transactions, provider API, results)
- `tests/`

## Installation

### Windows

```bash
git clone https://github.com/YukioE/payjoin-detector.git
cd payjoin-detector
python -m venv .venv
.venv\Scripts\activate
python -m pip install .
```

### Linux / macOS

```bash
git clone https://github.com/YukioE/payjoin-detector.git
cd payjoin-detector
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install .
```

> Optional: use `python -m pip install -e .` for an editable development install

After installation, the `payjoin-detector` command will be available while the virtual environment (`.venv`) is active, to deactivate run `deactivate`.

## Configuration

**Recommended setup**: run your own Bitcoin Core node and point the detector at a local [electrs API](https://github.com/Blockstream/electrs) instance. This avoids API rate limits and is the most reliable option for block and neighbour analysis. For the detection of single txs using public mempool or blockstream APIs is sufficient.

Create a `.toml` file and use it in addition to a subcommand (`payjoin-detector tx <txid> --config <file>`.

an example configuration is available under [sample_config.toml](./sample_config.toml)

```toml
# default values
[provider]
type = "electrs" # "electrs" | "bitcoin-core"
async = false

[electrs]
url = "https://mempool.space/api"

[bitcoin_core]
url = ""
user = ""
password = ""

[block]
threshold = 0.1

[output]
csv_file = ""
debug_file = ""
html_file = ""
```

CLI flags override values specified inside the config file.

example: `payjoin-detector tx <txid> --config <file> --csv_file output.csv`

> List of CLI flags:
>
> --config \<file>
>
> --provider \<provider> (either electrs or bitcoin-core)
>
> --electrs-url \<url>
>
> --rpc-url \<url>
>
> --rpc-user \<user>
>
> --rpc-password \<password>
>
> --async
>
> --threshold <0.0-1.0>
>
> --csv-output <file.csv>
>
> --debug-output <file.log>
>
> --html-output <file.html>

## Usage

For convenience, all commands have short aliases:

- `transaction` or `tx`
- `block` or `bl`
- `neighbours` or `nb`

### Analyze a transaction

```bash
payjoin-detector transaction <txid>

TX         : https://mempool.space/tx/bfd61c60ddfbba68217284a9ee3e777c753b92ac50677655c8a65033ab15efc9?mode=details
I / O      : 3 / 2
Confidence : 46.82%
  [+] Unnecessary input heuristic: UIH2 smallest output (31689 sat) > smallest input (4037 sat)
  [+] Small I/O counts heuristic: I/O count is 3/2
  [+] Mixed input types heuristic: all inputs same type - v0_p2wpkh
  [+] Mixed output types heuristic: all outputs same type - v0_p2wpkh
  [ ] Address reuse heuristic: no address reuse detected
  [-] Round fee heuristic: fee rate 30.08 sat/vb is non-round
  [+] Round output heuristic: all outputs non-round
  [ ] Round payment assignment heuristic: TX does not have exactly 2 inputs and 2 outputs
  [ ] CoinJoin pattern heuristic: not enough inputs/outputs to be CoinJoin (need >=5 each)
  [ ] nSequence asymmetry heuristic: all inputs have same nSequence - 4294967293
  [+] Signature asymmetry heuristic: signature asymmetry detected - {0: 'high-R', 1: 'high-R', 2: 'low-R'}
```

### Analyze a block

```bash
payjoin-detector block <blockhash>

Block      : https://mempool.space/block/00000000000000000001b94547385af991606982a7b3acb8e90d86bcb433fa00
------------------------------------------------------------
Total txs       : 4295
Above threshold : 35 (0.8%) [>= 10%]
------------------------------------------------------------

TX         : https://mempool.space/tx/2f8fe79d2c8831c29665139ebf00bd1ced40cfc721dc95bb664d2f3e04beb9a6?mode=details
I / O      : 2 / 2
Confidence : 58.18%
  [+] Unnecessary input heuristic: UIH2 smallest output (3909 sat) > smallest input (1325 sat)

  ...34 more transactions...
```

### Analyze transaction neighbours

```bash
payjoin-detector neighbours <txid>

── target ──

TX         : https://mempool.space/tx/bfd61c60ddfbba68217284a9ee3e777c753b92ac50677655c8a65033ab15efc9?mode=details
I / O      : 3 / 2
Confidence : 46.82%
  [+] Unnecessary input heuristic: UIH2 smallest output (31689 sat) > smallest input (4037 sat)
    ...

── prevout:in[0] ──

TX         : https://mempool.space/tx/eb861ecb371ffec5bd2df132c9afff2289b88eb0e299c9199ef4575f3d02d56f?mode=details
I / O      : 1 / 2
Confidence : 15.00%
  [ ] Unnecessary input heuristic: UIH1 optimal change detected, smallest output (75770 sat) < smallest input (1082483 sat)
    ...

── prevout:in[1] ──

TX         : https://mempool.space/tx/ebbf996b4d7e7b21471139c35149982566d9d532e82e180cf048c76bbf20d1ed?mode=details
I / O      : 5 / 2
Confidence : 30.91%
  [ ] Unnecessary input heuristic: UIH1 optimal change detected, smallest output (4037 sat) < smallest input (16951 sat)
    ...
```

> recommended to use with --html-output <file.html> or a config specifying an html output

## Heuristics

short description of each heuristic used, see `src/payjoin_detector/heuristics/` for actual implementations

1. **Input/Output Counts**
   - PayJoin requires ≥2 inputs (sender + receiver both contribute)
   - Single-input transactions are impossible for PayJoin
   - Typical PayJoins have ≥2 outputs (payment + change)

2. **Address Diversity (Inputs & Outputs)**
   - At least 2 distinct addresses required on input side and output side
   - If all inputs belong to one address, they're from the same entity (same case as 1., impossible for PayJoin)
   - Same logic applies to outputs—if they're all the same, no change separation is possible

3. **Cluster Separation**
   - Uses address clustering (CIOH - Common Input Ownership Heuristic) to identify whether inputs/outputs belong to different entities
   - Addresses clustered together suggest common ownership
   - PayJoin by definition involves inputs from different clusters (sender cluster vs. receiver cluster)
   - Note: This heuristic ironically trusts CIOH, which PayJoin is designed to break

4. **Round Fee Rate**
   - Per BIP 78, most wallets create round fee rates for consistency and predictability
   - PayJoin follows this pattern to avoid standing out—after adding receiver input, it adjusts the fee to maintain roundness
   - Non-round fee rates suggest single-wallet behavior

5. **Non-Round Outputs**
   - In normal transactions: if payment is round, change becomes non-round (one round, one non-round output)
   - In PayJoin: output = Sender Input + Receiver Input - Payment - Fee. Since inputs are non-round and independent, the result is almost always non-round
   - Getting two round outputs requires both receiver input AND payment to be round (rare coincidence)

6. **Mixed Input Types**
   - Pre-September 2024: BIP 78 prohibited mixed input types; homogeneous types were mandatory
   - Mixed types before this date are a strong signal against PayJoin
   - Post-September 2024: BIP 78 was updated to allow mixed types, enabling cooperation between different wallet versions

7. **CoinJoin Pattern Detection**
   - PayJoin's goal is anonymity without being obviously a privacy protocol
   - CoinJoins are flagged by blockchain analysts and have inputs/outputs removed from clustering
   - A transaction that looks like a CoinJoin (5+ inputs, 5+ outputs, many duplicate amounts) is avoided by PayJoin implementations
   - This heuristic excludes obvious CoinJoins from PayJoin scoring

8. **Unnecessary Input Heuristic - UIH2**
   - UIH1 (Optimal Change): The smallest output is smaller than the smallest input—suggests change detection
   - UIH2: The smallest output is LARGER than the smallest input—unexpected, suggests two independent wallets
   - When UIH2 is broken, it means even without the smallest input, the smallest output could still be paid
   - Receiver typically contributes a small input; if that's smaller than any output, it's a PayJoin signal
   - Some receiver implementations check for UIH1 and try to select appropriate inputs; others don't, creating this pattern

9. **Address Reuse**
   - Normal wallet best practice: use a new address for each transaction
   - Reused addresses are poor privacy hygiene and uncommon in modern wallets
   - Slight negative score if address reuse is detected (weak PayJoin signal, but possible with careless wallets)

10. **Round Payment Assignment**
    - Analyzes each input/output pair to check if `output_value - input_value` is round
    - For 2-input/2-output transactions, hidden round payments can reveal sender intent
    - If one assignment produces a round payment and the other doesn't, the round one is likely the actual payment
    - Suggests structured wallet behavior vs. the randomness of adding an arbitrary receiver input

11. **Signature Asymmetry**
    - Some wallets grind ECDSA signatures to a specific length (71 bytes = low R value)
    - Others don't grind and produce either 71 (low R) or 72 (high R) bytes randomly (~50/50)
    - A transaction with both low-R and high-R signatures could indicate multiple wallets, each with different signature strategies

12. **nSequence Asymmetry**
    - Most wallets set the same sequence value for all their inputs (no reason to vary it)
    - Receiver PayJoin implementations typically either enforce matching sequence values or fail
    - Different sequence values across inputs suggest multiple independent wallets
