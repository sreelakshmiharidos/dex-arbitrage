from __future__ import annotations

"""
swap_simulation.py

Implements AMM swap logic using Uniswap V2 formula.

- computes output for a single swap
- simulates multi-step swaps across a cycle
"""

from decimal import Decimal

# Uniswap V2 fee (0.3%)
FEE = Decimal("0.003")
ONE = Decimal("1")


def get_amount_out(
    amount_in: Decimal,
    reserve_in: Decimal,
    reserve_out: Decimal,
    fee: Decimal = FEE,
) -> Decimal:
  """
  Uniswap V2-style AMM output formula.

  amount_in_with_fee = amount_in * (1 - fee)
  amount_out = (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)
  """
  # Invalid input produces no output
  if amount_in <= 0:
    return Decimal("0")

  # Invalid reserves → unusable pool
  if reserve_in <= 0 or reserve_out <= 0:
    return Decimal("0")

  # Apply trading fee
  amount_in_with_fee = amount_in * (ONE - fee)
  denominator = reserve_in + amount_in_with_fee

  # Prevent division by zero
  if denominator == 0:
    return Decimal("0")

  return (amount_in_with_fee * reserve_out) / denominator


def simulate_cycle_edges(
    edges: list[dict[str, object]],
    amount_in: Decimal,
    fee: Decimal = FEE,
) -> Decimal:
  """
  Simulate a full cycle given a list of directed edges.
  """
  # Start with initial input amount
  amount = amount_in

  for edge in edges:
    reserve_in = edge["reserve_in"]
    reserve_out = edge["reserve_out"]

    # Ensure reserves are correct type
    if not isinstance(reserve_in, Decimal) or not isinstance(reserve_out, Decimal):
      raise TypeError("reserve_in and reserve_out must be Decimal values")

    # Perform swap for this edge
    amount = get_amount_out(amount, reserve_in, reserve_out, fee=fee)

    # If swap collapses to zero, stop early
    if amount <= 0:
      return Decimal("0")

  return amount