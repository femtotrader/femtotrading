#!/usr/bin/env python

from abc import ABCMeta, abstractmethod


class AbstractPositionSizer(object):
    """
    The AbstractPositionSizer abstract class handles sizing
    of an order
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def size_order(self, portfolio, initial_order):
        raise NotImplementedError("Should implement size_order()")
