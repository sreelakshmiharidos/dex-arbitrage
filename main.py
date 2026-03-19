from __future__ import annotations

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
  print("=" * 100)
  print("DEX Arbitrage Detection Summary")
  print("=" * 100)
  print(f"Filtered pools loaded: {total_pools}")
  print(f"Graph nodes:           {graph_nodes}")
  print(f"Profitable cycles:     {len(opportunities)}")
  print("=" * 100)

  for i, opportunity in enumerate(opportunities[:top_n], start=1):
    cycle = cast(list[str], opportunity["cycle"])
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

  print("Loading pools...")
  pools = load_pools(data_path, min_reserve_usd=min_reserve_usd)
  print(f"Loaded {len(pools)} filtered pools.")

  print("Building graph...")
  graph = build_graph(pools)
  print(f"Built graph with {len(graph)} nodes.")

  print("Finding triangular arbitrage opportunities...")
  opportunities = find_triangular_arbitrage_deduped(graph)

  print("Ranking opportunities...")
  ranked = rank_opportunities(opportunities)

  print_summary(
    total_pools=len(pools),
    graph_nodes=len(graph),
    opportunities=ranked,
    top_n=10,
  )

  output_path = Path("top_opportunities.txt")

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