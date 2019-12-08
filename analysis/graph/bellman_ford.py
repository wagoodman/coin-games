from collections import deque, Counter
from heapq import heappush, heappop
from itertools import count

from typing import Type, Dict, Tuple, Optional

import networkx as nx


def bellman_ford(G: Type[nx.DiGraph], source: str, weight_index: str='weight') -> Tuple[Dict[str, Optional[int]], Dict[str, Optional[int]]]:
    """
    Computes shortest paths from a single source vertex to all of the other vertices in a weighted digraph (allowing for negative weights).
    """

    if source not in G:
        raise KeyError("Node %s is not found in the graph" % source)

    dist = {source: 0}
    pred = {source: None}

    if len(G) == 1:
        return pred, dist

    if G.is_multigraph():
        def get_weight(edge_dict):
            return min(eattr.get(weight_index, 1) for eattr in list(edge_dict.values()))
    else:
        def get_weight(edge_dict):
            return edge_dict.get(weight_index, 1)

    if G.is_directed():
        G_succ = G.succ
    else:
        G_succ = G.adj

    inf = float('inf')
    n = len(G)

    count = {}
    q = deque([source])
    in_q = set([source])

    while q:
        u = q.popleft()
        in_q.remove(u)
        # Skip relaxations if the predecessor of u is in the queue.
        if pred[u] not in in_q:
            dist_u = dist[u]
            for v, e in list(G_succ[u].items()):
                dist_v = dist_u + get_weight(e)
                if dist_v < dist.get(v, inf):
                    if v not in in_q:
                        q.append(v)
                        in_q.add(v)
                        count_v = count.get(v, 0) + 1
                        if count_v == n:
                            q.remove(v)
                            continue
                        count[v] = count_v
                    dist[v] = dist_v
                    pred[v] = u

    return pred, dist



