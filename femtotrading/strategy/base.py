#!/usr/bin/env python

from abc import ABCMeta  # , abstractmethod
from munch import Munch


class StrategyParameters(Munch):
    pass


class AbstractStrategy(object):
    """
    AbstractStrategy is an abstract base class providing an interface for
    all subsequent (inherited) strategy handling objects.

    The goal of a (derived) Strategy object is to generate Signal
    objects for particular symbols based on the inputs of ticks
    generated from a PriceHandler (derived) object.

    This is designed to work both with historic and live data as
    the Strategy object is agnostic to data location.
    """

    __metaclass__ = ABCMeta

    default_params = StrategyParameters()

    def __init__(self, events_queue, tickers, **params):
        self.events_queue = events_queue
        self.tickers = tickers
        self.params = self.default_params
        # overwrite default_params using keyword arguments params
        for key in params.keys():
            self.params[key] = params[key]

    def on_init(self):
        """
        Strategy initialization
        """
        print("%s.on_init with %s" % (self.__class__.__name__, self.params))

    def on_tick(self, event):
        """
        What strategy does when TickEvent occurs
        """
        pass

    def on_bar(self, event):
        """
        What strategy does when BarEvent occurs
        """
        pass

    def on_signal(self, event):
        """
        What strategy does when SignalEvent occurs
        """
        pass

    def on_order(self, event):
        """
        What strategy does when OrderEvent occurs
        """
        pass

    def on_fill(self, event):
        """
        What strategy does when FillEvent occurs
        """
        pass

    def on_deinit(self):
        """
        Strategy deinitialization
        """
        print("%s.on_deinit" % (self.__class__.__name__))


class Strategies(AbstractStrategy):
    """
    Strategies is a collection of strategy
    """
    def __init__(self, *strategies):
        self._lst_strategies = strategies

    def on_init(self):
        for strategy in self._lst_strategies:
            strategy.on_init()

    def on_tick(self, event):
        for strategy in self._lst_strategies:
            strategy.on_tick(event)

    def on_bar(self, event):
        for strategy in self._lst_strategies:
            strategy.on_tick(event)

    def on_signal(self, event):
        for strategy in self._lst_strategies:
            strategy.on_signal(event)

    def on_order(self, event):
        for strategy in self._lst_strategies:
            strategy.on_signal(event)

    def on_fill(self, event):
        for strategy in self._lst_strategies:
            strategy.on_signal(event)

    def on_deinit(self):
        for strategy in self._lst_strategies:
            strategy.on_deinit()
