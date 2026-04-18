# Python PayJoin Detector

A lightweight tool to detect potential PayJoin transactions using heuristic analysis.

## Features

- Detect PayJoin likelihood for:
  - Single transactions
  - Entire blocks

- Pluggable providers:
  - Esplora API
  - Bitcoin Core RPC

- Heuristic-based scoring system (0.0 → 1.0 confidence)
- Optional CSV + debug logging

---

## Installation

```bash
git clone https://github.com/YukioE/payjoin-detector.git
cd payjoin-detector\src
```

---

## Configuration (optional)

Create a `.toml` file and use with `--config <path to .toml>`:

```toml
[provider]
type = "esplora" # "esplora" | "bitcoin-core" default: esplora

[esplora]
url = "https://mempool.space/api" # default: mempool

[bitcoin_core]
rpc_url  = "http://127.0.0.1:8332" # default: no url
rpc_user = "user" # default: no user
rpc_password = "password" # default: no password

[block]
threshold = 0.2 # default: 0.1
async     = true # default: false

[output]
csv_file = "results.csv" # default: no csv output
debug_file = "debug.log" # default: no debug file
```

CLI arguments override config values, comment lines using `#` to use default values

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

- remember that most online apis have limits on their usage, even fetching a block with just 1000 tx and no async behaviour will most likely hit those limits. It is recommended to use your own Bitcoin Core node since its much faster than online apis.

---

## How it works

1. Fetch transaction(s) from a provider
2. Run a set of heuristics
3. Aggregate scores into a confidence value

---

## Output

Each transaction returns:

- `txid`
- `input_count`
- `output_count`
- `confidence` (0.0–1.0)
- heuristic signals

Block analysis also reports:

- total transactions
- number above threshold
