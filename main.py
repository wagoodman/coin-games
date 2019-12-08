#!/usr/bin/env python

import time
from exchange.api.poloniex import Poloniex
from analysis.arbitrage_detector import ArbitrageDetector

def main(period=10):

    poloniex_client = Poloniex()

    while True:
        # get current currency exchange rate
        exchange_rates = poloniex_client.exchange_rates()
        arbitrage = ArbitrageDetector(exchange_rates=exchange_rates)
        path, profit_ratio = arbitrage.discover(root_currency="BTC")

        print(profit_ratio, path)

        time.sleep(period)

if __name__ == '__main__':
    main()