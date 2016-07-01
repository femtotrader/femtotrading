#!/usr/bin/env/python

"""
Test examples

One example can be test individually using:

$ nosetests -s -v examples/test_examples.py:TestExamples.test_buy_and_hold_backtest

"""
import unittest

from femtotrading import settings
import examples.main
import examples.buy_and_hold_backtest
import examples.mac_backtest
import examples.strategy_backtest


class TestExamples(unittest.TestCase):
    """
    Test example are executing correctly
    """
    def setUp(self):
        """
        Set up configuration.
        """
        self.config = settings.TEST
        self.testing = True

    # def test_main(self):
    #     """
    #     Test main
    #     """
    #     tickers = ["GBPUSD", "EURUSD"]
    #     n = 100000
    #     n_window = 5
    #     results = examples.main.run(settings.TEST_FX, self.testing, tickers, n, n_window)
    #     self.assertEqual(results, None)

    def test_buy_and_hold_backtest(self):
        """
        Test buy_and_hold
        Bar 0, at 2010-01-04 00:00:00
        Bar 1628, at 2016-06-22 00:00:00
        """
        tickers = ["SP500TR"]
        results = examples.buy_and_hold_backtest.run(self.config, self.testing, tickers)
        for (key, expected) in [
            ('sharpe', 0.5969),
            ('max_drawdown_pct', 5.0308),
            ('max_drawdown', 30174.01)
        ]:
            value = float(results[key])
            self.assertAlmostEqual(expected, value)
        for (key, expected) in [
                ('equity_returns', {'min': -1.6027, 'max': 1.2553, 'first': 0.0000, 'last': -0.0580}),
                ('drawdowns', {'min': 0.0, 'max': 30174.01, 'first': 0.0, 'last': 4537.02}),
                ('equity', {'min': 488958.0, 'max': 599782.01, 'first': 500000.0, 'last': 595244.99})]:
            values = results[key]
            self.assertAlmostEqual(float(min(values)), expected['min'])
            self.assertAlmostEqual(float(max(values)), expected['max'])
            self.assertAlmostEqual(float(values.iloc[0]), expected['first'])
            self.assertAlmostEqual(float(values.iloc[-1]), expected['last'])

    def test_mac_backtest(self):
        """
        Test mac_backtest
        """
        tickers = ["SP500TR"]
        results = examples.mac_backtest.run(self.config, self.testing, tickers)
        self.assertAlmostEqual(float(results['sharpe']), 0.6018)

    def test_strategy_backtest(self):
        """
        Test strategy_backtest
        """
        tickers = ["GOOG"]
        results = examples.strategy_backtest.run(self.config, self.testing, tickers)
        self.assertAlmostEqual(float(results['sharpe']), -7.5299)
