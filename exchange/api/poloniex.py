from typing import Dict, Any, Type, List
import datetime

import requests

from exchange.rate import ExchangeRate


class Poloniex:
    endpoint = "https://poloniex.com/public"

    def _api_query(self, command: str , params: Dict[str, Any] = {}) -> Dict[str, Any]:

        if command not in ("returnTicker", "returnChartData", "return24Volume"):
            raise RuntimeError(f"unsupported command: {command}")

        local_params = {'command': command, **params}

        response = requests.get(self.endpoint, params=local_params)
        response.raise_for_status()
        return response.json()

    # todo: mypy
    def chart_data(self, currencyPair: str, start: Type[datetime.datetime], end: Type[datetime.datetime], period: Type[datetime.timedelta]):
        return self._api_query("returnChartData", params={'currencyPair': currencyPair, 'start': start, 'end': end, 'period': period})

    def exchange_rates(self) -> List[ExchangeRate]:
        rates = self._api_query("returnTicker")

        results = []
        for currency_pair, info in rates.items():
            origin, target = currency_pair.split("_")
            rate = info["last"]

            results.append(ExchangeRate(origin=origin, target=target, rate=float(rate)))

        return results
