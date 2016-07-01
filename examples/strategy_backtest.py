#!/usr/bin/env/python

import click

from decimal import Decimal

from femtotrading.event import EventsQueue
from femtotrading.data_iterator import HistoricCSVTickIterator
from femtotrading.trading_session import Backtest
from femtotrading.execution_handler import IBSimulatedExecutionHandler
from femtotrading.portfolio_handler import PortfolioHandler
from femtotrading.position_sizer import FixedQuantityPositionSizer
from femtotrading.risk_manager import ExampleRiskManager
from femtotrading.statistics import SimpleStatistics
from femtotrading.compliance import ExampleCompliance
from femtotrading import settings
from femtotrading.strategy import ExampleStrategy


def run(config, testing, tickers):
    # Set up variables needed for backtest
    events_queue = EventsQueue()
    csv_dir = config.CSV_DATA_DIR
    initial_equity = Decimal("500000.00")
    # heartbeat = 0.0
    # max_iters = 10000000000

    # Use Historic CSV Price iterator
    price_handler = HistoricCSVTickIterator(csv_dir, tickers)

    # Use the Example Strategy
    strategy = ExampleStrategy(events_queue, tickers)

    # Use an example Position Sizer
    position_sizer = FixedQuantityPositionSizer(100)

    # Use an example Risk Manager
    risk_manager = ExampleRiskManager()

    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(
        events_queue, initial_equity, price_handler,
        position_sizer, risk_manager
    )

    # Use the TestCompliance component
    compliance = ExampleCompliance(config)

    # Use a simulated IB Execution Handler
    execution_handler = IBSimulatedExecutionHandler(
        events_queue, price_handler, compliance
    )
    # Use the default Statistics
    statistics = SimpleStatistics(portfolio_handler)

    # Set up the backtest
    backtest = Backtest(
        events_queue, tickers, price_handler, strategy,
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
@click.option('--tickers', default='GOOG', help='Tickers (use comma)')
def main(config, testing, tickers):
    tickers = tickers.split(',')
    config = settings.from_file(config, testing)
    run(config, testing, tickers)


if __name__ == "__main__":
    main()
