#!/usr/bin/env/python

from .base import (TradingSession, TradingSessionType)


class Live(TradingSession):
    @property
    def type(self):
        return TradingSessionType.LIVE
