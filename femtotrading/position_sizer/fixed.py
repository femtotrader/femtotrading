#!/usr/bin/env python

from .base import AbstractPositionSizer


class FixedQuantityPositionSizer(AbstractPositionSizer):
    def __init__(self, default_quantity):
        self.default_quantity = default_quantity

    def size_order(self, portfolio, initial_order):
        """
        This FixedPositionSizer object simply modifies
        the quantity to be default_quantity (100) of
        any share transacted.
        """
        initial_order.quantity = self.default_quantity
        return initial_order
