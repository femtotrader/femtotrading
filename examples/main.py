#!/usr/bin/env/python

import click

from decimal import Decimal

from femtotrading import settings
from femtotrading.event import EventsQueue
from femtotrading.data_iterator import MonthlyCSVTickIterator
from femtotrading.strategy import (Strategies, PrintStrategy)
from femtotrading.position_sizer import FixedQuantityPositionSizer
from femtotrading.risk_manager import ExampleRiskManager
from femtotrading.portfolio_handler import PortfolioHandler
from femtotrading.compliance import ExampleCompliance
from femtotrading.execution_handler import IBSimulatedExecutionHandler
from femtotrading.statistics import SimpleStatistics
from femtotrading.trading_session import Backtest


def run(config, testing, tickers, n, n_window):
    events_queue = EventsQueue()

    csv_dir = config.CSV_DATA_DIR
    initial_equity = Decimal("500000.00")

    if n_window < 0:
        n_window = len(tickers) + 3

    # Use Historic CSV Price iterator
    data_iterator = MonthlyCSVTickIterator(tickers, csv_dir, 2014, 1)

    strategy = PrintStrategy(events_queue, tickers)
    # strategy = Strategies(PrintStrategy(events_queue, tickers))

    # Use an example Position Sizer
    position_sizer = FixedQuantityPositionSizer(100)

    # Use an example Risk Manager
    risk_manager = ExampleRiskManager()

    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(
        events_queue, initial_equity, data_iterator,
        position_sizer, risk_manager
    )

    # Use the ExampleCompliance component
    compliance = ExampleCompliance(config)

    # Use a simulated IB Execution Handler
    execution_handler = IBSimulatedExecutionHandler(
        events_queue, data_iterator, compliance
    )

    # Use the default Statistics
    statistics = SimpleStatistics(portfolio_handler)

    # Set up the backtest
    backtest = Backtest(
        events_queue, tickers, data_iterator, strategy,
        portfolio_handler,
        execution_handler,
        position_sizer, risk_manager,
        statistics,
    )
    results = backtest.run(testing=testing)
    return results


@click.command()
@click.option('--config', default=settings.DEFAULT_CONFIG_FILENAME, help='Config filename')
@click.option('--testing/--no-testing', default=False, help='Enable testing mode')
@click.option('--tickers', default='GBPUSD,EURUSD', help='Tickers (use comma)')
@click.option('--n', default=10000, help='Display only every N')
@click.option('--n_window', default=5, help='Display window')
def main(config, testing, tickers, n, n_window):
    tickers = tickers.split(",")

    config = settings.from_file(config, testing)

    if n <= 0:
        n = -1

    params = (config, testing, tickers, n, n_window)

    run(*params)


if __name__ == '__main__':
    main()
