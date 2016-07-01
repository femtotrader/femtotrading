#!/usr/bin/env/python

from .base import (TradingSession, TradingSessionType)


class PaperTrade(TradingSession):
    @property
    def type(self):
        return TradingSessionType.PAPERTRADE
