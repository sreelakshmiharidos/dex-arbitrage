from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path
from typing import Any

getcontext().prec = 50


def _to_decimal(value: Any) -> Decimal:
  """Convert a JSON numeric/string value to Decimal."""
  return Decimal(str(value))


def normalize_pool(raw_pool: dict[str, Any]) -> dict[str, Any] | None:
  """
  Normalize one raw pool record into a flat structure.

  Returns None if the row is malformed or unusable.
  """
  try:
    pool_id = raw_pool["id"]

    token0 = raw_pool["token0"]["id"]
    token1 = raw_pool["token1"]["id"]

    decimals0 = int(raw_pool["token0"]["decimals"])
    decimals1 = int(raw_pool["token1"]["decimals"])

    reserve0 = _to_decimal(raw_pool["reserve0"])
    reserve1 = _to_decimal(raw_pool["reserve1"])
    reserve_usd = _to_decimal(raw_pool.get("reserveUSD", "0"))

    if reserve0 <= 0 or reserve1 <= 0:
      return None

    if token0 == token1:
      return None

    return {
      "pool_id": pool_id,
      "token0": token0,
      "token1": token1,
      "decimals0": decimals0,
      "decimals1": decimals1,
      "reserve0": reserve0,
      "reserve1": reserve1,
      "reserve_usd": reserve_usd,
    }
  except (KeyError, TypeError, ValueError, InvalidOperation):
    return None


def load_pools(
    json_path: str | Path,
    min_reserve_usd: Decimal = Decimal("100"),
) -> list[dict[str, Any]]:
  """
  Load, normalize, and filter pools from the JSON file.
  """
  path = Path(json_path)

  with path.open("r", encoding="utf-8") as f:
    raw_pools = json.load(f)

  normalized_pools = []
  for raw_pool in raw_pools:
    pool = normalize_pool(raw_pool)
    if pool is None:
      continue

    if pool["reserve_usd"] < min_reserve_usd:
      continue

    normalized_pools.append(pool)

  return normalized_pools