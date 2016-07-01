#!/usr/bin/env/python

import six
import os

from .base import AbstractTickDataIterator, DefaultDataParser

from ..priority_queue import UPriorityQueue
from ..compat import queue
from ..data import Data, TickerData
from ..event import TickEvent


class MonthlyTickerTickIterator(object):
    """
    Yields ticks for ONE ticker for a given month
    """
    def __init__(self, ticker, data_dir, year, month, data_parser=None):
        self.data_dir = data_dir
        self.ticker = ticker
        self.year = year
        self.month = month
        fname = self.filename
        print("open '%s'" % fname)
        self._fd = open(fname)
        self._eof = False
        if data_parser is None:
            self._parser = DefaultDataParser()
        else:
            self._parser = data_parser

    @property
    def filename(self):
        return os.path.join(
            os.path.expanduser(self.data_dir),
            "%s-%4d-%02d.csv" % (self.ticker, self.year, self.month)
        )

    def __next__(self):
        if not self._eof:
            line = self._fd.readline()
            if not line:
                self.__close__()
                raise StopIteration
            data = line[0:-1]  # remove \n
            data = data.split(",")
            dt = self._parser.datetime(data[1])
            ticker_data = TickerData([
                # ("ticker", data[0]),
                # ("dt", dt),
                ("bid", self._parser.price(data[2])),
                ("ask", self._parser.price(data[3])),
                # ("volume", self._parser.default.volume),
            ])
            # ticker_data["spread"] = (ticker_data["ask"] - ticker_data["bid"]) * 10000
            return dt, ticker_data

    @property
    def done(self):
        return self._eof

    def __close__(self):
        print("close %s" % self)
        self._eof = True
        self._fd.close()

    def __repr__(self):
        s = "<MonthTickDefaultIterator %s %04d %02d>" % (self.ticker, self.year, self.month)
        return s


class MonthlyCSVTickIterator(AbstractTickDataIterator):
    """
    Yields ticks for SEVERAL tickers for a given month
    """
    def __init__(self, tickers, data_dir, year, month, tick_ticker_iterator=MonthlyTickerTickIterator):
        self.data_dir = data_dir
        if isinstance(tickers, six.string_types):
            self.tickers = [tickers]
        else:
            self.tickers = tickers
        self._pq = UPriorityQueue(len(tickers))  # priority queue / heap queue
        self.d_iterators = {}
        self.i_ticker = 0
        for ticker in tickers:
            print("Create iterator for '%s'" % ticker)
            self.d_iterators[ticker] = tick_ticker_iterator(ticker, data_dir, year, month)
        self.last_data = Data()  # ticker=>ticker_data

    def __next__(self):
        try:
            for ticker in self.tickers:
                if ticker not in self._pq.keys():
                    ticker_itr = self.d_iterators[ticker]
                    if not ticker_itr.done:
                        dt, ticker_data = ticker_itr.__next__()
                        if ticker_data is None:
                            continue
                        self.last_data[ticker] = ticker_data
                        # dt, cur_ticker, ask, bid, vol = ticker_data
                        # dt, = ticker_data
                        # dt = ticker_data["dt"]
                        self._pq.enqueue(ticker, dt)

            dt = self._pq.next_priority
            tickers_to_process = self._pq.dequeues()

            data = Data()  # Ticker=>ticker_data
            for ticker in tickers_to_process:
                ticker_data = self.last_data[ticker]
                # dt = ticker_data[1]
                data[ticker] = ticker_data
            # dt = self.last_data[tickers_to_process[0]]["dt"]
            return TickEvent(dt, data)

        except StopIteration:
            dt, data = self.__next__()
            return TickEvent(dt, data)

        except queue.Empty:
            raise StopIteration

    # @property
    # def done(self):
    #     flag = True
    #    for ticker in self.tickers:
    #        if not self.d_iterators[ticker].done:
    #            return False
    #    return flag

    def __close__(self):
        for ticker in self.tickers:
            self.d_iterators[ticker].__close__()
