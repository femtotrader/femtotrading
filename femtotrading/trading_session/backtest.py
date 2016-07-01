#!/usr/bin/env/python

import time

from .base import TradingSession

from ..event import (TickEvent, BarEvent, SignalEvent, OrderEvent, FillEvent)
from ..debug import ensure_dt_increasing
from ..compat import queue


class Backtest(TradingSession):
    """
    Encapsulates the settings and components for
    carrying out an event-driven backtest.
    """
    def _loop(self):
        """
        Carries out an infinite while loop that polls the
        events queue and directs each event to either the
        strategy component of the execution handler. The
        loop will then pause for "heartbeat" seconds and
        continue until the maximum number of iterations is
        exceeded.
        """
        for iters, event in enumerate(self.data_handler):
            self.iters = iters  # for loop
            if iters >= self.max_iters:
                break

            self.cur_time = event.time

            # asserts for debug
            assert ensure_dt_increasing(self.cur_time, self.prev_time)

            if isinstance(event, TickEvent):
                self.strategies.on_tick(event)
                self.portfolio_handler.on_tick(event)
                self.statistics.on_tick(event)
                self.ticks += 1

            elif isinstance(event, BarEvent):
                self.strategies.on_bar(event)
                self.portfolio_handler.on_bar(event)
                self.statistics.on_bar(event)
                self.bars += 1

            while True:  # len(self.events_queue) > 0:
                try:
                    event = self.events_queue.dequeue()

                    if isinstance(event, SignalEvent):
                        print("%s" % event)
                        self.strategies.on_signal(event)
                        self.portfolio_handler.on_signal(event)
                    elif isinstance(event, OrderEvent):
                        print("%s" % event)
                        self.strategies.on_order(event)
                        self.execution_handler.on_order(event)
                    elif isinstance(event, FillEvent):
                        print("%s" % event)
                        self.strategies.on_fill(event)
                        self.portfolio_handler.on_fill(event)
                    else:
                        raise NotImplemented("Unsupported event.type '%s'" % event.type)
                except queue.Empty:
                    break

            time.sleep(self.heartbeat)
            self.prev_time = self.cur_time
            # self.iters += 1  # while loop

    @property
    def isbacktest(self):
        return True

    @property
    def islivetest(self):  # paper trade
        return False

    @property
    def islivetrade(self):
        return False
