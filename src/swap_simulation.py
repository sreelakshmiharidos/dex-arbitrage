from __future__ import annotations

from decimal import Decimal

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
  if amount_in <= 0:
    return Decimal("0")

  if reserve_in <= 0 or reserve_out <= 0:
    return Decimal("0")

  amount_in_with_fee = amount_in * (ONE - fee)
  denominator = reserve_in + amount_in_with_fee

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
  amount = amount_in

  for edge in edges:
    reserve_in = edge["reserve_in"]
    reserve_out = edge["reserve_out"]

    if not isinstance(reserve_in, Decimal) or not isinstance(reserve_out, Decimal):
      raise TypeError("reserve_in and reserve_out must be Decimal values")

    amount = get_amount_out(amount, reserve_in, reserve_out, fee=fee)

    if amount <= 0:
      return Decimal("0")

  return amount