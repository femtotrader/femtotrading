#!/usr/bin/env/python

import datetime
import decimal
from enum import Enum

from ..utils import EPOCH


DataIteratorType = Enum("DataIteratorType", "TICK BAR")


class DefaultDataParser(object):
    def __init__(self):
        class Default:
            volume = 0.0
            price = 0.0
            datetime = EPOCH

        self.default = Default

    def price(self, s):
        return float(s)

    def volume(self, s):
        return float(s)

    def datetime(self, s):
        return datetime.datetime(
            year=int(s[0:4]),  # yyyy
            month=int(s[4:6]),  # mm
            day=int(s[6:8]),  # dd
            hour=int(s[9:11]),  # HH
            minute=int(s[12:14]),  # MM
            second=int(s[15:17]),  # SS
            microsecond=int(s[18:]) * 1000  # sss
        )


class DecimalDataParser(DefaultDataParser):
    def price(self, s):
        return decimal.Decimal(s)

    def volume(self, s):
        return decimal.Decimal(s)


class AbstractDataIterator(object):
    """
    AbstractDataIterator is base class providing an interface for all subsequent
    (inherited) data (price) events
    """
    @property
    def type(self):
        raise NotImplementedError("Must be implemented")

    def on_init(self):
        pass

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def isa(self, type):
        return self.type == type

    def unsubscribe_ticker(self, ticker):
        """
        Unsubscribes the price handler from a current ticker symbol.
        """
        try:
            self.tickers.pop(ticker, None)
            self.tickers_data.pop(ticker, None)
        except KeyError:
            print(
                "Could not unsubscribe ticker %s "
                "as it was never subscribed." % ticker
            )

    def get_timestamp(self, ticker):
        """
        Returns the most recent actual timestamp for a given ticker
        """
        if ticker in self.tickers:
            timestamp = self.tickers[ticker]["timestamp"]
            return timestamp
        else:
            print(
                "Timestamp for ticker %s is not "
                "available from the %s." % (ticker, self.__class__.__name__)
            )
            return None


class AbstractTickDataIterator(AbstractDataIterator):
    """
    AbstractDataIterator is base class providing an interface for all subsequent
    (inherited) tick data (price) events
    """
    @property
    def type(self):
        return DataIteratorType.TICK


class AbstractBarDataIterator(AbstractDataIterator):
    """
    AbstractDataIterator is base class providing an interface for all subsequent
    (inherited) bar data (price) events
    """
    @property
    def type(self):
        return DataIteratorType.BAR
