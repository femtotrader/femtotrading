#!/usr/bin/env/python

from .base import TradingSession


class PaperTrade(TradingSession):
    @property
    def isbacktest(self):
        return False

    @property
    def islivetest(self):  # paper trade
        return True

    @property
    def islivetrade(self):
        return False
