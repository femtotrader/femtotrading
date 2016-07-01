#!/usr/bin/env python

import datetime
import os
import csv

from .base import Compliance


class ExampleCompliance(Compliance):
    """
    A basic compliance module which writes trades to a
    CSV file in the output directory.
    """

    def __init__(self, config):
        """
        Wipe the existing trade log for the day, leaving only
        the headers in an empty CSV.

        It allows for multiple backtests to be run
        in a simple way, but quite likely makes it unsuitable for
        a production environment that requires strict record-keeping.
        """
        # Remove the previous CSV file
        self.config = config
        today = datetime.datetime.utcnow().date()
        self.csv_filename = "tradelog_" + today.strftime("%Y-%m-%d") + ".csv"
        directory = os.path.expanduser(self.config.OUTPUT_DIR)
        if not os.path.exists(directory):
            print("Create directory %s." % self.config.OUTPUT_DIR)
            os.makedirs(directory)
        try:
            fname = os.path.join(directory, self.csv_filename)
            os.remove(fname)
        except (IOError, OSError):
            print("No tradelog files to clean.")

        # Write new file header
        fieldnames = [
            "timestamp", "ticker",
            "action", "quantity",
            "exchange", "price",
            "commission"
        ]
        fname = os.path.expanduser(os.path.join(self.config.OUTPUT_DIR, self.csv_filename))
        with open(fname, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    def record_trade(self, fill):
        """
        Append all details about the FillEvent to the CSV trade log.
        """
        fname = os.path.expanduser(os.path.join(self.config.OUTPUT_DIR, self.csv_filename))
        with open(fname, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                fill.timestamp, fill.ticker,
                fill.action, fill.quantity,
                fill.exchange, fill.price,
                fill.commission
            ])
