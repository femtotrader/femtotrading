#!/usr/bin/env/python

from .compat import queue
from .data import Data, TickerData


class EventsQueue(object):
    def __init__(self, block=False):
        self._block = block
        self._q = queue.Queue()

    def enqueue(self, event):
        return self._q.put(event, block=self._block)

    def dequeue(self):
        return self._q.get(block=self._block)

    def __len__(self):
        return self._q.qsize()


class AbstractEvent(object):
    """
    AbstractEvent is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    @property
    def typename(self):
        return self.__class__.__name__


class AbstractTimedEvent(AbstractEvent):
    """
    AbstractTimedEvent is base class providing an interface for all subsequent
    (inherited) timed events
    """
    def __init__(self, time, data_event):
        """
        Initialises the TimedEvent.
        """
        self.time = time
        self.data_event = data_event

    def __str__(self):
        return "Time: %s, %s %s" % (self.time, self.typename, self.data_event)

    def __repr__(self):
        return str(self)

    def have(self, ticker):
        return ticker in self.data_event.keys()

    def __getitem__(self, ticker):
        return self.data_event[ticker]


class TickEvent(AbstractTimedEvent):
    """
    Handles the event of receiving a new market update tick,
    which is defined as a ticker symbol and associated best
    bid and ask from the top of the order book.
    """
    def __str__(self):
        return "Time: %s, %s %s" % (self.time, self.typename, self.data_event)

    @classmethod
    def from_ticker(cls, dt, ticker, bid, ask):
        return TickEvent(dt, Data({ticker: TickerData({"bid": bid, "ask": ask})}))


class BarEvent(AbstractTimedEvent):
    """
    Handles the event of receiving a new market
    open-high-low-close-volume bar, as would be generated
    via common data providers such as Yahoo Finance.
    """
    def __init__(self, time, period, data_event):
        """
        Initialises the BarEvent.
        """
        self.time = time
        self.period = period
        self.data_event = data_event

    @classmethod
    def from_ticker(cls, dt, period, ticker, ticker_data):
        return BarEvent(dt, period, Data({ticker: ticker_data}))

    def __str__(self):
        return "Time: %s, %s %s, %s" % (self.time, self.typename, self.period, self.data_event)

    @classmethod
    def from_df(cls, dt, ticker, row):
        evt = BarEvent(dt, Data({ticker: TickerData(row)}))
        return evt

    @classmethod
    def from_panel(cls, dt, row_data):
        data = Data()
        for k, v in row_data.iteritems():
            data[k] = TickerData(v)
        evt = BarEvent(dt, data)
        return evt


class SignalEvent(AbstractEvent):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """
    def __init__(self, ticker, action):
        """
        Initialises the SignalEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'GOOG'.
        action - 'BOT' (for long) or 'SLD' (for short).
        """
        self.ticker = ticker
        self.action = action

    def __str__(self):
        format_str = "<%14s Ticker: '%s', Action: '%s'>" % (
            self.__class__.__name__, self.ticker, self.action
        )
        return format_str

    def __repr__(self):
        return str(self)


class OrderEvent(AbstractEvent):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a ticker (e.g. GOOG), action (BOT or SLD)
    and quantity.
    """
    def __init__(self, ticker, action, quantity):
        """
        Initialises the OrderEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'GOOG'.
        action - 'BOT' (for long) or 'SLD' (for short).
        quantity - The quantity of shares to transact.
        """
        self.ticker = ticker
        self.action = action
        self.quantity = quantity

    def __str__(self):
        format_str = "<%14s Ticker: '%s', Action: '%s', Quantity: %s>" % (
            self.__class__.__name__, self.ticker,
            self.action, self.quantity
        )
        return format_str

    def __repr__(self):
        return str(self)


class FillEvent(AbstractEvent):
    """
    Encapsulates the notion of a filled order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.

    TODO: Currently does not support filling positions at
    different prices. This will be simulated by averaging
    the cost.
    """
    def __init__(
        self, timestamp, ticker,
        action, quantity,
        exchange, price,
        commission
    ):
        """
        Initialises the FillEvent object.

        timestamp - The timestamp when the order was filled.
        ticker - The ticker symbol, e.g. 'GOOG'.
        action - 'BOT' (for long) or 'SLD' (for short).
        quantity - The filled quantity.
        exchange - The exchange where the order was filled.
        price - The price at which the trade was filled
        commission - The brokerage commission for carrying out the trade.
        """
        self.timestamp = timestamp
        self.ticker = ticker
        self.action = action
        self.quantity = quantity
        self.exchange = exchange
        self.price = price
        self.commission = commission

    def __str__(self):
        format_str = "<%14s @ %s Ticker: '%s', Action: '%s', Quantity: %s, " \
            "Exchange: %s Price: %s Commission: %s>" % (
                self.__class__.__name__, self.timestamp, self.ticker,
                self.action, self.quantity,
                self.exchange, self.price, self.commission
            )
        return format_str

    def __repr__(self):
        return str(self)
