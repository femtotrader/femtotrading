#!/usr/bin/env/python

import click

from femtotrading import settings

from femtotrading.data_iterator.monthly_csv_tick import MonthlyCSVTickIterator
from femtotrading.data_iterator.historic_csv_tick import HistoricCSVTickIterator
from femtotrading.data_iterator.yahoo_daily_csv_bar import YahooDailyCSVBarIterator


def run(config, testing, tickers, data_iterator):
    csv_dir = config.CSV_DATA_DIR

    # Use Historic CSV Price Handler
    l_data_iterator = data_iterator.lower()
    if l_data_iterator == 'MonthlyCSVTick'.lower():
        data_iterator = MonthlyCSVTickIterator(tickers, csv_dir, 2014, 1)  # config.TEST_FX tickers="GBPUSD,EURUSD"
    elif l_data_iterator == 'HistoricCSVTick'.lower():
        data_iterator = HistoricCSVTickIterator(csv_dir, tickers)  # config.TEST_EQUITIES tickers="GOOG"
    elif l_data_iterator == 'YahooDailyCSVBar'.lower():
        data_iterator = YahooDailyCSVBarIterator(csv_dir, tickers)  # config.TEST_EQUITIES tickers="SP500TR"
    else:
        raise NotImplementedError("Unsupported data_iterator: %s" % data_iterator)

    for data in data_iterator:
        print(data)


@click.command()
@click.option('--config', default=settings.DEFAULT_CONFIG_FILENAME, help='Config filename')
@click.option('--testing/--no-testing', default=False, help='Enable testing mode')
@click.option('--tickers', default='GBPUSD,EURUSD', help='Tickers')
@click.option('--data_iterator', default='MonthlyCSVTick', help='Tick or Bar price iterator')
def main(config, testing, tickers, data_iterator):
    tickers = tickers.split(',')
    config = settings.from_file(config, testing)
    run(config, testing, tickers, data_iterator)


if __name__ == "__main__":
    main()
