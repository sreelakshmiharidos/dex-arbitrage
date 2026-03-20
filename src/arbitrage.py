from __future__ import annotations

"""
arbitrage.py

Core arbitrage logic:
- finds triangular cycles
- deduplicates equivalent cycles
- tests multiple trade sizes
- returns profitable opportunities
"""

from decimal import Decimal
from typing import Any

from src.swap_simulation import simulate_cycle_edges


def canonicalize_cycle_nodes(cycle: list[str]) -> tuple[str, ...]:
  """
  Convert [A, B, C, A] into a rotation-invariant tuple like (A, B, C).
  Cycles equivalent up to rotation map to the same key.
  """
  # Remove duplicate closing node (A at the end)
  core = cycle[:-1]

  # Generate all cyclic rotations of the cycle
  rotations = [tuple(core[i:] + core[:i]) for i in range(len(core))]

  # Pick the lexicographically smallest rotation as canonical form
  return min(rotations)


def get_candidate_trade_sizes(edges: list[dict[str, Any]]) -> list[Decimal]:
  """
  Generate a small set of candidate trade sizes from the smallest reserve_in
  in the cycle.

  This is a heuristic to avoid absurd trades on tiny liquidity.
  """
  # Find bottleneck liquidity (smallest pool in the cycle)
  min_reserve_in = min(edge["reserve_in"] for edge in edges)

  # Ignore extremely small trades
  min_trade_size = Decimal("1")

  # Fractions of liquidity to try
  fractions = [
    Decimal("0.0001"),
    Decimal("0.0005"),
    Decimal("0.001"),
    Decimal("0.005"),
    Decimal("0.01"),
  ]

  candidates = []
  seen = set()

  for fraction in fractions:
    # Scale trade size based on liquidity
    amount = min_reserve_in * fraction

    # Skip if too small
    if amount < min_trade_size:
      continue

    # Normalize Decimal for deduplication
    key = str(amount.normalize())
    if key in seen:
      continue

    seen.add(key)
    candidates.append(amount)

  return candidates


def evaluate_cycle_with_best_trade_size(
    edges: list[dict[str, Any]],
    cycle_nodes: list[str],
) -> dict[str, Any] | None:
  """
  Evaluate one cycle by testing a few candidate input sizes and keeping
  the best profitable one.
  """
  best_result = None

  for amount_in in get_candidate_trade_sizes(edges):
    # Simulate swaps across the cycle
    final_amount = simulate_cycle_edges(edges, amount_in)

    # Compute profit
    profit = final_amount - amount_in

    # Ignore non-profitable trades
    if profit <= 0:
      continue

    # Compute percentage return
    profit_pct = (profit / amount_in) * Decimal("100")

    result = {
      "cycle": cycle_nodes,
      "amount_in": amount_in,
      "final_amount": final_amount,
      "profit": profit,
      "profit_pct": profit_pct,
      "edges": edges,
    }

    # Keep best result by absolute profit
    if best_result is None or result["profit"] > best_result["profit"]: # type: ignore
      best_result = result

  return best_result


def find_triangular_arbitrage_deduped(
    graph: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
  """
  Find triangular arbitrage cycles A -> B -> C -> A.

  - Deduplicates equivalent rotations
  - Evaluates each cycle with a small trade-size search
  """
  opportunities = []
  seen_cycles = set()

  for token_a in graph:
    for edge_ab in graph[token_a]:
      token_b = edge_ab["to"]

      for edge_bc in graph.get(token_b, []):
        token_c = edge_bc["to"]

        # Skip immediate backtracking A -> B -> A
        if token_c == token_a:
          continue

        for edge_ca in graph.get(token_c, []):
          if edge_ca["to"] != token_a:
            continue

          # Construct full cycle
          cycle_nodes = [token_a, token_b, token_c, token_a]

          # Canonical key for deduplication
          cycle_key = canonicalize_cycle_nodes(cycle_nodes)

          if cycle_key in seen_cycles:
            continue

          seen_cycles.add(cycle_key)

          # Evaluate this cycle
          edges = [edge_ab, edge_bc, edge_ca]
          best_result = evaluate_cycle_with_best_trade_size(edges, cycle_nodes)

          # Store only profitable cycles
          if best_result is not None:
            opportunities.append(best_result)

  return opportunities


def rank_opportunities(
    opportunities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
  """
  Rank opportunities by absolute profit, descending.
  """
  return sorted(opportunities, key=lambda x: x["profit"], reverse=True)


def short_token(token: str) -> str:
  """
  Shorten a token address for nicer console printing.
  """
  return f"{token[:6]}...{token[-4:]}"