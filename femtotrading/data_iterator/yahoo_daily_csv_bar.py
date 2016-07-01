#!/usr/bin/env/python

import decimal
import os
from collections import OrderedDict

import pandas as pd

from .base import AbstractBarDataIterator
from ..event import BarEvent
from ..data import PLACES, TickerData


class YahooDailyCSVBarIterator(AbstractBarDataIterator):
    """
    YahooDailyCSVBarIterator is designed to read CSV files of
    Yahoo Finance daily Open-High-Low-Close-Volume (OHLCV) data
    for each requested financial instrument and to iterate
    BarEvents.
    """
    def __init__(self, csv_dir, init_tickers=None):
        """
        Takes the CSV directory and a possible
        list of initial ticker symbols then
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
        print(ticker_path)
        self.tickers_data[ticker] = pd.io.parsers.read_csv(
            ticker_path, header=0, parse_dates=True,
            index_col=0, names=(
                "Date", "Open", "High", "Low",
                "Close", "Volume", "Adj Close"
            )
        )
        self.tickers_data[ticker]["Ticker"] = ticker

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
                    "close": decimal.Decimal(str(row0["Close"])).quantize(PLACES[5]),
                    "adj_close": decimal.Decimal(str(row0["Adj Close"])).quantize(PLACES[5]),
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

    def get_last_close(self, ticker):
        """
        Returns the most recent actual (unadjusted) closing price.
        """
        if ticker in self.tickers:
            close_price = self.tickers[ticker]["close"]
            return close_price
        else:
            print(
                "Close price for ticker %s is not "
                "available from the %s." % (ticker, self.__class__.__name__)
            )
            return None

    def __next__(self):
        """
        Returns next BarEvent.
        """
        dt, row = next(self._stream)

        # Obtain all elements of the bar from the dataframe
        decimal.getcontext().rounding = decimal.ROUND_HALF_DOWN
        ticker = row["Ticker"]
        open_price = decimal.Decimal(str(row["Open"])).quantize(PLACES[5])
        high_price = decimal.Decimal(str(row["High"])).quantize(PLACES[5])
        low_price = decimal.Decimal(str(row["Low"])).quantize(PLACES[5])
        close_price = decimal.Decimal(str(row["Close"])).quantize(PLACES[5])
        adj_close_price = decimal.Decimal(str(row["Adj Close"])).quantize(PLACES[5])
        volume = int(row["Volume"])

        # Create decimalised prices for
        # closing price and adjusted closing price
        self.tickers[ticker]["close"] = close_price
        self.tickers[ticker]["adj_close"] = adj_close_price
        self.tickers[ticker]["timestamp"] = dt

        # Create the tick event for the queue
        period = 86400  # Seconds in a day
        tickerdata = TickerData([("open", open_price),
                                 ("high", high_price),
                                 ("low", low_price),
                                 ("close", close_price),
                                 ("volume", volume),
                                 ("adj_close", adj_close_price)])
        return BarEvent.from_ticker(dt, period, ticker, tickerdata)
