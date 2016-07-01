#!/usr/bin/env/python

from collections import deque

import numpy as np

from .base import AbstractStrategy, StrategyParameters
from ..event import SignalEvent


class MovingAverageCrossStrategy(AbstractStrategy):
    """
    Requires:
    short_window - Lookback period for short moving average
    long_window - Lookback period for long moving average
    """

    default_params = StrategyParameters({
        'short_window': 100,
        'long_window': 400
    })

    def on_init(self):
        super(MovingAverageCrossStrategy, self).on_init()
        self.short_window = self.default_params.short_window
        self.long_window = self.default_params.long_window
        self.bars = 0
        self.invested = False
        self.sw_bars = deque(maxlen=self.short_window)
        self.lw_bars = deque(maxlen=self.long_window)

    def on_bar(self, event):
        # TODO: Only applies SMA to first ticker
        ticker = self.tickers[0]

        if event.have(ticker):
            # Add latest adjusted closing price to the
            # short and long window bars
            self.lw_bars.append(event[ticker].adj_close)
            if self.bars > self.long_window - self.short_window:
                self.sw_bars.append(event[ticker].adj_close)

            # Enough bars are present for trading
            if self.bars > self.long_window:
                # Calculate the simple moving averages
                short_sma = np.mean(self.sw_bars)
                long_sma = np.mean(self.lw_bars)
                # Trading signals based on moving average cross
                if short_sma > long_sma and not self.invested:
                    print("LONG: %s" % event.time)
                    signal = SignalEvent(ticker, "BOT")
                    self.events_queue.enqueue(signal)
                    self.invested = True
                elif short_sma < long_sma and self.invested:
                    print("SHORT: %s" % event.time)
                    signal = SignalEvent(ticker, "SLD")
                    self.events_queue.enqueue(signal)
                    self.invested = False
            self.bars += 1
