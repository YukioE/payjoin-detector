# Python PayJoin Detector

A lightweight tool to detect potential PayJoin transactions using heuristic analysis.

## Repository overview

The project is a Python CLI app (`payjoin-detector`) that fetches Bitcoin transaction data from a provider and runs a set of heuristics to calculate a PayJoin confidence score.

- `src/payjoin_detector/main.py` - CLI entrypoint and command dispatch (`transaction`, `block`, `neighbours`)
- `src/payjoin_detector/cli/` - argument parsing, command handlers, output/debug formatting
- `src/payjoin_detector/detector.py` - core detection pipeline and heuristic orchestration
- `src/payjoin_detector/heuristics/` - individual heuristic implementations (one file per heuristic)
- `src/payjoin_detector/providers/` - data source adapters (currently Esplora and Bitcoin Core)
- `src/payjoin_detector/core/` - shared domain models and interfaces (transactions, provider API, results)
- `tests/`

## Installation

```bash
git clone https://github.com/YukioE/payjoin-detector.git
cd payjoin-detector
python -m pip install .
```

> Optional: editable install for development
>
> ```bash
> python -m venv .venv
> .venv\Scripts\activate
> python -m pip install -e .
> ```

## Configuration

Create a `.toml` file and use it with `--config <file>`. CLI flags override config values.

**Recommended setup**: run your own Bitcoin Core node and point the detector at a local [electrs API](https://github.com/Blockstream/electrs) instance. This avoids API rate limits and is the most reliable option for block and neighbour analysis. For the detection of single txs using public mempool or blockstream APIs is sufficient.

```toml
# default values
[provider]
type = "esplora" # "esplora" | "bitcoin-core"
async = false

[esplora]
url = "https://mempool.space/api"

[bitcoin_core]
rpc_url = ""
rpc_user = ""
rpc_password = ""

[block]
threshold = 0.1

[output]
csv_file = ""
debug_file = ""
html_file = ""
```

---

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
