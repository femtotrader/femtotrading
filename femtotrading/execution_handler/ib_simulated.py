#!/usr/bin/env python

from decimal import Decimal

from .base import ExecutionHandler
from ..event import FillEvent
from ..exceptions import EmptyQuantityError


class IBSimulatedExecutionHandler(ExecutionHandler):
    """
    The simulated execution handler for Interactive Brokers
    converts all order objects into their equivalent fill
    objects automatically without latency, slippage or
    fill-ratio issues.

    This allows a straightforward "first go" test of any strategy,
    before implementation with a more sophisticated execution
    handler.
    """

    def __init__(self, events_queue, data_iterator, compliance=None):
        """
        Initialises the handler, setting the event queue
        as well as access to local pricing.

        Parameters:
        events_queue - The Queue of Event objects.
        """
        self.events_queue = events_queue
        self.data_iterator = data_iterator
        self.compliance = compliance

    def calculate_ib_commission(self):
        """
        Calculate the Interactive Brokers commission for
        a transaction. At this stage, simply add in $1.00
        for transaction costs, irrespective of lot size.
        """
        return Decimal("1.00")

    def on_order(self, event):
        """
        Converts OrderEvents into FillEvents "naively",
        i.e. without any latency, slippage or fill ratio problems.

        Parameters:
        event - An Event object with order information.
        """
        # Obtain values from the OrderEvent
        ticker = event.ticker
        # timestamp = datetime.datetime.utcnow()  # ToFix: see https://github.com/mhallsmoore/qstrader/issues/27
        timestamp = self.data_iterator.get_timestamp(ticker)
        action = event.action
        if event.quantity == 0:
            raise EmptyQuantityError
        quantity = event.quantity

        # Obtain the fill price
        if self.data_iterator.is_tick():
            bid, ask = self.data_iterator.get_best_bid_ask(ticker)
            if event.action == "BOT":
                fill_price = Decimal(str(ask))
            else:
                fill_price = Decimal(str(bid))
        else:
            close_price = self.data_iterator.get_last_close(ticker)
            fill_price = Decimal(str(close_price))

        # Set a dummy exchange and calculate trade commission
        exchange = "ARCA"
        commission = self.calculate_ib_commission()

        # Create the FillEvent and place on the events queue
        fill_event = FillEvent(
            timestamp, ticker,
            action, quantity,
            exchange, fill_price,
            commission
        )
        self.events_queue.enqueue(fill_event)

        if self.compliance is not None:
            self.compliance.record_trade(fill_event)
