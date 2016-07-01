#!/usr/bin/env/python

from .base import TradingSession


class Live(TradingSession):
    @property
    def isbacktest(self):
        return False

    @property
    def islivetest(self):  # paper trade
        return False

    @property
    def islivetrade(self):
        return True
