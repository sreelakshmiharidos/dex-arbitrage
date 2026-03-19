# DEX Arbitrage Detection

This project implements an off-chain arbitrage detection system for Uniswap V2-style decentralized exchanges (DEXs).

The system constructs a token swap graph from pool data, detects triangular arbitrage cycles, simulates swaps using AMM formulas, and ranks the most profitable opportunities.

---

## 🚀 Features

- Load and normalize Uniswap V2 pool data
- Build a directed token swap graph
- Simulate swaps using constant-product AMM formula
- Detect triangular arbitrage cycles (A → B → C → A)
- Deduplicate equivalent cycles
- Estimate reasonable trade sizes
- Rank opportunities by simulated profit
- Output top-10 arbitrage cycles

---

## 📁 Project Structure

```

dex-arbitrage/
├── data/
│   └── v2pools.json
├── src/
│   ├── load_data.py
│   ├── graph.py
│   ├── swap_simulation.py
│   └── arbitrage.py
├── main.py
├── report.md
└── README.md

```

---

## ⚙️ How It Works

### 1. Data Loading
- Parses JSON pool data
- Filters invalid and low-liquidity pools (`reserveUSD < 100`)

### 2. Graph Construction
- Nodes = tokens
- Directed edges = swap paths
- Each pool creates two edges (bidirectional)

### 3. Swap Simulation
Uses Uniswap V2 formula:

```

amount_in_with_fee = amount_in × (1 - 0.003)

amount_out =
(amount_in_with_fee × reserve_out) /
(reserve_in + amount_in_with_fee)

````

### 4. Cycle Detection
- Searches triangular cycles (A → B → C → A)
- Avoids trivial backtracking
- Deduplicates equivalent cycles

### 5. Trade Size Estimation
- Tests multiple candidate sizes based on pool liquidity
- Applies a minimum trade size to avoid unrealistic micro-trades
- Selects the best-performing size per cycle

### 6. Ranking
- Ranks by absolute profit
- Outputs top-10 opportunities

---

## ▶️ Running the Project

From the project root:

```bash
python main.py
````

---

## 📊 Example Output

```
#1
Cycle:        0x761d...60f3 -> 0x95ad...c4ce -> 0xe64b...3286 -> 0x761d...60f3
Amount in:    2330167.35
Final amount: 2774798.36
Profit:       444631.01
Profit %:     19.08%
```

Results are also saved to:

```
top_opportunities.txt
```

---

## ⚠️ Limitations

* Uses static snapshot data (not real-time)
* No on-chain validation
* Only triangular cycles are considered
* Trade size selection is heuristic, not optimal
* Some data inconsistencies may still exist

---

## 🤖 AI Usage

AI tools (ChatGPT) were used to:

* Structure the project into modules
* Implement graph construction and simulation logic
* Design cycle detection and deduplication
* Improve trade-size heuristics
* Debug and refine the pipeline

Outputs were manually validated and adjusted to ensure correctness.

---

## 📌 Notes

This is a simulation-based approach. No real trades are executed.

The focus is on demonstrating:

* algorithm design
* graph modeling
* reasoning about AMM-based systems

```

---

# 💡 Why this README works

It:
- hits all task expectations
- is **easy to skim in <30 seconds**
- shows structure + clarity
- aligns with your report (important)
- looks like a strong internship submission

---