#!/usr/bin/env/python

"""
Work in progress

Iterating  over a Panel

see https://github.com/mhallsmoore/qstrader/issues/58

<class 'pandas.core.panel.Panel'>
Dimensions: 6 (items) x 1631 (major_axis) x 2 (minor_axis)
Items axis: Open to Adj Close
Major_axis axis: 2010-01-04 00:00:00 to 2016-06-24 00:00:00
Minor_axis axis: GOOG to IBM

"""

import pandas as pd
import pandas_datareader.data as web
import datetime
import requests_cache

from ..event import BarEvent
# from ..event import TickEvent
# from ..data import TickerData, Data


expire_after = datetime.timedelta(days=3)
session = requests_cache.CachedSession(cache_name='cache', backend='sqlite', expire_after=expire_after)
panel = web.DataReader(["GOOG", "IBM"], "yahoo", session=session)
pd.set_option("max_rows", 10)


def identity(*args):
    return args


def data_from_dataframe(df, ticker, f_event=None):
    if f_event is None:
        f_event = identity
    for (dt, row) in df.iterrows():
        yield(f_event(dt, ticker, row))


def data_from_panel(panel, f_event=None):
    if f_event is None:
        f_event = identity
    for dt, data in panel.transpose(1, 0, 2).iteritems():
        # for (ticker, bar) in data.iteritems():
        #     yield(dt, ticker, bar)
        yield(f_event(dt, data))

ticker = "GOOG"
df = panel[:, :, ticker]
# for (dt, ticker, bar) in data_from_dataframe(df, ticker):
#     print(dt, ticker, bar)

# for event in data_from_dataframe(df, ticker, BarEvent.from_df):
#     print(event)

# for (dt, ticker, bar) in data_from_panel(panel):
#     print(dt, ticker, bar)

# for (dt, ticker, bar) in data_from_panel(panel):
#     print(dt, ticker, bar)

for event in data_from_panel(panel, BarEvent.from_panel):
    print(event)

# for event in data_from_panel(panel, BarEvent.from_panel):
#     print(event)
