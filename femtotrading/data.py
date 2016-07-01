#!/usr/bin/env/python

import decimal
from collections import OrderedDict

PLACES = {
    2: decimal.Decimal("0.01"),
    5: decimal.Decimal("0.00001")
}


Data = OrderedDict

try:
    from munch import Munch
    # Data = Munch  # ToDo: OrderedMunch https://github.com/Infinidat/munch/issues/11
    TickerData = Munch
except ImportError:
    print("can't import Munch using dict")
    TickerData = dict
