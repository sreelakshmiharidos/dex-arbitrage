from __future__ import annotations

"""
main.py

Entry point for the arbitrage detection pipeline.

Steps:
1. Load pool data
2. Build graph
3. Find arbitrage cycles
4. Rank opportunities
5. Print and save results
"""

from decimal import Decimal
from pathlib import Path
from typing import cast

from src.arbitrage import find_triangular_arbitrage_deduped, rank_opportunities, short_token
from src.graph import build_graph
from src.load_data import load_pools


def print_summary(
    total_pools: int,
    graph_nodes: int,
    opportunities: list[dict[str, object]],
    top_n: int = 10,
) -> None:
  # Print header
  print("=" * 100)
  print("DEX Arbitrage Detection Summary")
  print("=" * 100)

  # Print dataset + results stats
  print(f"Filtered pools loaded: {total_pools}")
  print(f"Graph nodes:           {graph_nodes}")
  print(f"Profitable cycles:     {len(opportunities)}")
  print("=" * 100)

  # Print top opportunities
  for i, opportunity in enumerate(opportunities[:top_n], start=1):
    cycle = cast(list[str], opportunity["cycle"])

    # Shorten token addresses for readability
    pretty_cycle = " -> ".join(short_token(token) for token in cycle)

    print(f"#{i}")
    print(f"Cycle:        {pretty_cycle}")
    print(f"Amount in:    {opportunity['amount_in']}")
    print(f"Final amount: {opportunity['final_amount']}")
    print(f"Profit:       {opportunity['profit']}")
    print(f"Profit %:     {opportunity['profit_pct']}")
    print("-" * 100)


def main() -> None:
  data_path = Path("data") / "v2pools.json"
  min_reserve_usd = Decimal("100")

  # Step 1: Load pools
  print("Loading pools...")
  pools = load_pools(data_path, min_reserve_usd=min_reserve_usd)
  print(f"Loaded {len(pools)} filtered pools.")

  # Step 2: Build graph
  print("Building graph...")
  graph = build_graph(pools)
  print(f"Built graph with {len(graph)} nodes.")

  # Step 3: Find arbitrage cycles
  print("Finding triangular arbitrage opportunities...")
  opportunities = find_triangular_arbitrage_deduped(graph)

  # Step 4: Rank results
  print("Ranking opportunities...")
  ranked = rank_opportunities(opportunities)

  # Step 5: Print summary
  print_summary(
    total_pools=len(pools),
    graph_nodes=len(graph),
    opportunities=ranked,
    top_n=10,
  )

  output_path = Path("top_opportunities.txt")

  # Save top results to file
  with output_path.open("w", encoding="utf-8") as f:
    for i, opportunity in enumerate(ranked[:10], start=1):
      cycle = opportunity["cycle"]
      pretty_cycle = " -> ".join(short_token(token) for token in cycle)

      f.write(f"#{i}\n")
      f.write(f"Cycle:        {pretty_cycle}\n")
      f.write(f"Amount in:    {opportunity['amount_in']}\n")
      f.write(f"Final amount: {opportunity['final_amount']}\n")
      f.write(f"Profit:       {opportunity['profit']}\n")
      f.write(f"Profit %:     {opportunity['profit_pct']}\n")
      f.write("-" * 100 + "\n")

  print("Saved top opportunities to top_opportunities.txt")


if __name__ == "__main__":
  main()