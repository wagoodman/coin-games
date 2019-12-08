from typing import Dict, Any, List, Type
import json, urllib.request, urllib.error, urllib.parse, sys, math

import networkx as nx

from exchange.rate import ExchangeRate
from analysis.graph.bellman_ford import bellman_ford


CONV_IDX = 'weight'

def normalize(value):
    return -1.0 * math.log(value)

def denormalize(value):
    return math.exp(-1.0 * value)

# derived from algorith described here: https://math.stackexchange.com/questions/94414/an-algorithm-for-arbitrage-in-currency-exchange
class ArbitrageDetector(object):

    def __init__(self, exchange_rates: List[ExchangeRate]) -> None:
        self.success = False
        self.exchange_path, self.return_ratio = None, None
        self._build_graph(exchange_rates)


    def _build_graph(self, exchange_rates: List[ExchangeRate]):
        self.graph = nx.DiGraph()

        # {"cur1_cur2" : rate} , where rate is a multiplier of cur2 to cur1
        # converted into { ("cur1", "cur2") : rate }
        # Note: this is not directly used to search the graph, only for reference
        exchange_rate_lookup =  { (er.origin, er.target): er.rate for er in exchange_rates }

        forward_log_exchange_rate = [ (start, end, normalize(rate)) for (start, end), rate in list(exchange_rate_lookup.items()) ]
        self.graph.add_weighted_edges_from(forward_log_exchange_rate)

        # prune leaf nodes (as these cannot be used in a cycle
        leafNodes = [node for node, degree in list(self.graph.degree()) if degree < 2]
        self.graph.remove_nodes_from(leafNodes)

        # mirror exchange rates between all currencies with edges
        currencySet = set( self.graph.edges() )
        rev_currency_set = set( [ (end, start) for start, end in self.graph.edges() ] )
        rev_currency_set -= currencySet

        reverse_log_exchange_rate = [ (start, end, normalize( 1.0/exchange_rate_lookup[end,start] )) for start, end in rev_currency_set ]
        self.graph.add_weighted_edges_from(reverse_log_exchange_rate)

    def discover(self, root_currency):
        exchange_graph, cost = bellman_ford(self.graph, source=root_currency, weight_index=CONV_IDX)

        # no path found! report no profit...
        if exchange_graph[root_currency] == None:
            return [], 0

        # there is at least a good path!...

        visited = [root_currency]
        profit = 1.0
        next_node = exchange_graph[root_currency]

        current_node = root_currency
        while next_node not in visited:
            visited.append(next_node)
            profit *= denormalize(self.graph[next_node][current_node][CONV_IDX])
            current_node = next_node
            next_node = exchange_graph[next_node]

        profit *= denormalize(self.graph[root_currency][current_node][CONV_IDX])
        visited.append(root_currency)

        return visited, profit
