#!/usr/bin/env/python

from .base import AbstractStrategy
from ..event import SignalEvent, EventType

BAR = EventType.BAR


class BuyAndHoldStrategy(AbstractStrategy):
    """
    A testing strategy that simply purchases (longs) a set of
    assets upon first receipt of the relevant bar event and
    then holds until the completion of a backtest.
    """
    def on_init(self):
        super(BuyAndHoldStrategy, self).on_init()
        self.ticks = 0
        self.invested = False

    def on_bar(self, event):
        ticker = self.tickers[0]
        if event.have(ticker):
            if not self.invested and self.ticks == 0:
                signal = SignalEvent(ticker, "BOT")
                self.events_queue.enqueue(signal)
                self.invested = True
            self.ticks += 1
