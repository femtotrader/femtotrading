#!/usr/bin/env/python

from .base import AbstractStrategy
from ..event import SignalEvent


class ExampleStrategy(AbstractStrategy):
    """
    A testing strategy that alternates between buying and selling
    a ticker on every 5th tick. This has the effect of continuously
    "crossing the spread" and so will be loss-making strategy.

    It is used to test that the backtester/live trading system is
    behaving as expected.
    """
    def on_init(self):
        super(ExampleStrategy, self).on_init()
        self.ticks = 0
        self.invested = False

    def on_tick(self, event):
        ticker = self.tickers[0]
        if event.have(ticker):
            if self.ticks % 5 == 0:
                if not self.invested:
                    signal = SignalEvent(ticker, "BOT")
                    self.events_queue.enqueue(signal)
                    self.invested = True
                else:
                    signal = SignalEvent(ticker, "SLD")
                    self.events_queue.enqueue(signal)
                    self.invested = False
            self.ticks += 1
