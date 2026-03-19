from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any


def build_graph(pools: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
  """
  Build a directed graph from pools.

  Each pool contributes two directed edges:
  token0 -> token1
  token1 -> token0
  """
  graph: dict[str, list[dict[str, Any]]] = defaultdict(list)

  for pool in pools:
    token0 = pool["token0"]
    token1 = pool["token1"]
    reserve0: Decimal = pool["reserve0"]
    reserve1: Decimal = pool["reserve1"]
    pool_id = pool["pool_id"]

    graph[token0].append({
      "from": token0,
      "to": token1,
      "pool_id": pool_id,
      "reserve_in": reserve0,
      "reserve_out": reserve1,
    })

    graph[token1].append({
      "from": token1,
      "to": token0,
      "pool_id": pool_id,
      "reserve_in": reserve1,
      "reserve_out": reserve0,
    })

  return dict(graph)