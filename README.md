# Python PayJoin Detector

A lightweight tool to detect potential PayJoin transactions using heuristic analysis.

## Features

- Detect PayJoin likelihood for:
  - Single transactions
  - Entire blocks
  - Transaction neighbours (prevouts and outspends)

- Pluggable providers:
  - Esplora API
  - Bitcoin Core RPC

- Heuristic-based scoring system (0.0 → 1.0 confidence)
- Optional CSV, debug logging, and HTML neighbour reports

---

## Installation

```bash
git clone https://github.com/YukioE/payjoin-detector.git
cd payjoin-detector\src
```

---

## Configuration (optional)

Create a `.toml` file and use it with `--config <file>`. CLI flags override config values.

Recommended setup: run your own Bitcoin Core node and point the detector at a local Blockstream/electrs (Esplora-compatible) instance. This avoids API rate limits and is the most reliable option for block and neighbour analysis.

```toml
[provider]
type = "esplora" # "esplora" | "bitcoin-core" default: esplora
async = true # default: false

[esplora]
url = "https://mempool.space/api" # default: mempool

[bitcoin_core]
rpc_url = "http://127.0.0.1:8332" # default: no url
rpc_user = "user" # default: no user
rpc_password = "password" # default: no password

[block]
threshold = 0.2 # default: 0.1

[output]
csv_file = "results.csv" # default: no csv output
debug_file = "debug.log" # default: no debug file
html_file = "report.html" # default: no html report
```

---

## Usage

### Analyze a transaction

```bash
python -m payjoin_detector tx <txid>
```

### Analyze a block

```bash
python -m payjoin_detector block <blockhash>
```

### Analyze transaction neighbours

```bash
python -m payjoin_detector neighbours <txid> --html-output report.html
```

### Common options

- `--config <file>`: load provider/output defaults from TOML
- `--provider esplora|bitcoin-core`: choose the backend
- `--async`: fetch transactions in parallel
- `--csv-output <file>`: append `txid,confidence` rows
- `--debug-output <file>`: write debug logs
- `--threshold <0.0-1.0>`: block confidence cutoff
- `--html-output <file>`: save neighbour analysis as HTML

---

## Output

- `tx`: txid, input/output counts, confidence, heuristic signals
- `block`: block summary plus all transactions above the threshold
- `neighbours`: console report or HTML report for prevouts/outspends

---

## How it works

1. Fetch transaction(s) from a provider
2. Run a set of heuristics
3. Aggregate scores into a confidence value
