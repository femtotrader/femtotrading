#!/usr/bin/env/python

from ..utils import EPOCH


class TradingSession(object):
    """
    Encapsulates the settings and components for
    carrying out an event-driven backtest / papertrade / livetrade.
    """
    def __init__(
        self, events_queue, tickers, data_handler, strategies,
        portfolio_handler,
        execution_handler,
        position_sizer, risk_manager,
        statistics,
        heartbeat=0.0, max_iters=10000000000
    ):
        """
        Set up the backtest variables according to
        what has been passed in.
        """

        self.events_queue = events_queue  # data_handler.events_queue

        self.tickers = tickers
        self.data_handler = data_handler
        self.strategies = strategies

        self.portfolio_handler = portfolio_handler
        self.execution_handler = execution_handler
        self.position_sizer = position_sizer
        self.risk_manager = risk_manager
        self.statistics = statistics

        self.heartbeat = heartbeat
        self.max_iters = max_iters

        self.cur_time = None

        self.equity = portfolio_handler.initial_cash

        self.testing = False

    def run(self, testing=False):
        self.testing = testing
        results = self._run()
        return results
        # duration = timeit.timeit(self._run, number=1)
        # print("%s executed in %.3fs" % (self.typename, duration))

    def _run(self):
        self._on_init()
        try:
            self._loop()
        except KeyboardInterrupt:
            print("%s halt by KeyboardInterrupt" % self.typename)
        return self._on_deinit()

    def _on_init(self):
        print("Running %s..." % self.typename)
        self.iters = 0
        self.ticks = 0
        self.bars = 0
        self.prev_time = EPOCH  # previous data event time
        self.data_handler.on_init()
        self.strategies.on_init()

    def _on_deinit(self):
        print("End of %s..." % self.typename)
        self.strategies.on_deinit()
        results = self.statistics.get_results()
        print("Backtest complete.")
        print("Sharpe Ratio: %s" % results["sharpe"])
        print("Max Drawdown: %s" % results["max_drawdown"])
        print("Max Drawdown Pct: %s" % results["max_drawdown_pct"])
        if not self.testing:
            self.statistics.plot_results()
        return results

    @property
    def typename(self):
        return self.__class__.__name__

    def islive(self):
        return self.islivetest() or self.islivetrade()
