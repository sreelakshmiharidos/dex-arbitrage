# DEX Arbitrage Detection — Report

## Overview

This project implements an off-chain arbitrage detection system for Uniswap V2-style AMM pools.

The goal is to:
- Construct a token swap graph
- Detect profitable arbitrage cycles
- Rank the most profitable opportunities
- Suggest a reasonable trade size for execution

This solution focuses on triangular arbitrage cycles (A → B → C → A).

---

## Graph Construction

The dataset consists of a snapshot of Uniswap V2 pools.

Each pool contains:
- token0, token1
- reserves
- USD liquidity

We construct a directed graph where:
- Nodes = tokens
- Edges = swap directions

Each pool creates two directed edges:
- token0 → token1
- token1 → token0

Each edge stores:
- reserve_in
- reserve_out
- pool_id

This allows simulation of swaps in either direction.

---

## Swap Modeling

Swaps are modeled using the Uniswap V2 constant-product formula:

amount_in_with_fee = amount_in × (1 - fee)

amount_out =  
(amount_in_with_fee × reserve_out) / (reserve_in + amount_in_with_fee)

A fee of 0.3% is applied per swap.

For a cycle, swaps are simulated sequentially across all edges.

---

## Cycle Detection

We detect triangular cycles of the form:

A → B → C → A

The algorithm:
1. Iterate over all tokens A
2. Explore neighbors B
3. Explore neighbors C of B
4. Check if a path exists back to A

To avoid duplicates:
- Cycles are canonicalized (rotation-invariant)
- Only unique cycles are evaluated

---

## Trade Size Selection

Instead of using a fixed input size, we estimate a reasonable trade size:

- For each cycle, we compute candidate trade sizes based on:
  - small fractions of the minimum reserve_in across edges

- We also enforce a minimum trade size (≥ 1 unit) to:
  - avoid unrealistic micro-trades
  - reduce noise from low-liquidity distortions

For each candidate size:
- simulate the cycle
- compute profit
- select the best-performing size

---

## Ranking Metric

Cycles are ranked by:

**Absolute profit = final_amount − initial_amount**

Additional metrics computed:
- profit percentage
- final output amount

Top-10 opportunities are printed and saved to file.

---

## Results

After filtering and deduplication:
- Pools used: ~8000
- Graph nodes: ~6600
- Profitable cycles: ~200+

The system outputs the top 10 most profitable triangular arbitrage opportunities.

---

## Limitations

- Uses static snapshot data (not real-time)
- No on-chain validation
- Only triangular cycles (no longer paths)
- Trade size selection is heuristic, not optimal
- Some price inconsistencies may still exist due to data artifacts

---

## AI Usage

AI tools (ChatGPT) were used extensively to:

- Structure the project into modular components
- Design graph construction logic
- Implement swap simulation
- Develop cycle detection and deduplication
- Improve trade-size heuristics
- Debug issues and refine outputs

Limitations encountered:
- Type hint warnings required manual interpretation
- Initial outputs included unrealistic profits, requiring heuristic adjustments
- Care was needed to ensure correctness beyond generated code

All outputs were manually reviewed and refined to ensure correctness.

---

## Conclusion

This project successfully demonstrates off-chain detection of arbitrage opportunities in AMM-based DEXs.

It builds a scalable pipeline from raw pool data to ranked arbitrage opportunities, with reasonable trade-size estimation and practical filtering.