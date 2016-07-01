#!/usr/bin/env python

from abc import ABCMeta, abstractmethod


class Statistics(object):
    """
    Statistics is an abstract class providing an interface for
    all inherited statistic classes (live, historic, custom, etc).

    The goal of a Statistics object is to keep a record of useful
    information about one or many trading strategies as the strategy
    is running. This is done by hooking into the main event loop and
    essentially updating the object according to portfolio performance
    over time.

    Ideally, Statistics should be subclassed according to the strategies
    and timeframes-traded by the user. Different trading strategies
    may require different metrics or frequencies-of-metrics to be updated,
    however the example given is suitable for longer timeframes.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_results(self):
        """
        Return a dict containing all statistics.
        """
        raise NotImplementedError("Should implement get_results()")

    @abstractmethod
    def plot_results(self):
        """
        Plot all statistics collected up until 'now'
        """
        raise NotImplementedError("Should implement plot_results()")

    def on_tick(self, tick_event):
        """
        Update all the statistics according to values of the portfolio
        and open positions. This should be called from within the
        event loop when TickEvent occurs.
        """
        self._update(tick_event.time)

    def on_bar(self, bar_event):
        """
        Update all the statistics according to values of the portfolio
        and open positions. This should be called from within the
        event loop when BarEvent occurs.
        """
        self._update(bar_event.time)
