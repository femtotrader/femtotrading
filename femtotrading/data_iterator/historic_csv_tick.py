#!/usr/bin/env/python

import decimal
import os
import pandas as pd

from collections import OrderedDict

from .base import AbstractTickDataIterator

from ..event import TickEvent
from ..data import PLACES


class HistoricCSVTickIterator(AbstractTickDataIterator):
    """
    HistoricCSVTickIterator is designed to read CSV files of
    tick data for each requested financial instrument and
    and to iterate TickEvents.
    """
    def __init__(self, csv_dir, init_tickers=None):
        """
        Takes the CSV directory and a possible
        list of initial ticker symbols
        """
        self.csv_dir = csv_dir
        self.tickers = OrderedDict()
        self.tickers_data = OrderedDict()
        self.init_tickers = init_tickers

    def on_init(self):
        """
        creates an (optional) list of ticker subscriptions and
        associated prices.
        """
        if self.init_tickers is not None:
            for ticker in self.init_tickers:
                self.subscribe_ticker(ticker)
        self._stream = self._merge_sort_ticker_data()

    def _open_ticker_price_csv(self, ticker):
        """
        Opens the CSV files containing the equities ticks from
        the specified CSV data directory, converting them into
        them into a pandas DataFrame, stored in a dictionary.
        """
        ticker_path = os.path.join(self.csv_dir, "%s.csv" % ticker)
        self.tickers_data[ticker] = pd.io.parsers.read_csv(
            ticker_path, header=0, parse_dates=True,
            dayfirst=True, index_col=1,
            names=("Ticker", "Time", "Bid", "Ask")
        )

    def _merge_sort_ticker_data(self):
        """
        Concatenates all of the separate equities DataFrames
        into a single DataFrame that is time ordered, allowing tick
        data events to be added to the queue in a chronological fashion.

        Note that this is an idealised situation, utilised solely for
        backtesting. In live trading ticks may arrive "out of order".
        """
        return pd.concat(
            self.tickers_data.values()
        ).sort_index().iterrows()

    def subscribe_ticker(self, ticker):
        """
        Subscribes the price handler to a new ticker symbol.
        """
        if ticker not in self.tickers:
            try:
                self._open_ticker_price_csv(ticker)
                dft = self.tickers_data[ticker]
                row0 = dft.iloc[0]
                ticker_prices = {
                    "bid": decimal.Decimal(str(row0["Bid"])),
                    "ask": decimal.Decimal(str(row0["Ask"])),
                    "timestamp": dft.index[0]
                }
                self.tickers[ticker] = ticker_prices
            except OSError:
                print(
                    "Could not subscribe ticker %s "
                    "as no data CSV found for pricing." % ticker
                )
        else:
            print(
                "Could not subscribe ticker %s "
                "as is already subscribed." % ticker
            )

    def get_best_bid_ask(self, ticker):
        """
        Returns the most recent bid/ask price for a ticker.
        """
        if ticker in self.tickers:
            bid = self.tickers[ticker]["bid"]
            ask = self.tickers[ticker]["ask"]
            return bid, ask
        else:
            print(
                "Bid/ask values for ticker %s are not "
                "available from the %s." % (ticker, self.__class__.__name__)
            )
            return None, None

    def __next__(self):
        """
        Return the next TickEvent.
        """
        dt, row = next(self._stream)

        decimal.getcontext().rounding = decimal.ROUND_HALF_DOWN
        ticker = row["Ticker"]
        bid = decimal.Decimal(str(row["Bid"])).quantize(PLACES[5])
        ask = decimal.Decimal(str(row["Ask"])).quantize(PLACES[5])

        # Create decimalised prices for traded pair
        self.tickers[ticker]["bid"] = bid
        self.tickers[ticker]["ask"] = ask
        self.tickers[ticker]["timestamp"] = dt

        # Create the tick event for the queue
        return TickEvent.from_ticker(dt, ticker, bid, ask)
