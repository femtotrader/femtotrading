#!/usr/bin/env/python

import time

from .base import AbstractStrategy, StrategyParameters

from ..profiling import s_speed


class DisplayStrategy(AbstractStrategy):
    """
    A strategy which display ticks / bars

    params:
        n = 10000
        n_window = 5
    """

    default_params = StrategyParameters({
        'n': 10000,
        'n_window': 5
    })

    def on_init(self):
        super(DisplayStrategy, self).on_init()
        self.i = 0
        self.t0 = time.time()

    def on_tick(self, event):
        self._on_price_event(event)

    def on_bar(self, event):
        self._on_price_event(event)

    def _on_price_event(self, event):
        n = self.params.n
        n_window = self.params.n_window
        if self.i % n == 0 and self.i != 0:
            print(s_speed(event, self.i, self.t0))
            print("")
        if self.i % n in range(n_window):
            print("%d %s" % (self.i, event))
        self.i += 1
