#!/usr/bin/env python

from abc import ABCMeta, abstractmethod


class AbstractRiskManager(object):
    """
    AbstractRiskManager object refine an order
    to handle risk.
    """
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def refine_orders(self, portfolio, sized_order):
        raise NotImplementedError("Should implement refine_orders()")
