import datetime
from event import EventType
from strategy_base import AbstractStrategy


class TestStrategy(AbstractStrategy):
    '''
    A testing strategy that simply purchases (longs) an asset upon first receipt of the relevant bar event and then
    holds until the completion of a backtest.
    '''
    def __init__(self, ticker, events_que, base_quantity=100):
        self.ticker = ticker
        self.events_queue = events_que
        self.base_quantity = base_quantity
        self.bars = 0
        self.invested = False

    def calculate_signals(self, event):
        if event.type in [EventType.BAR, EventType.TICK] and event.ticker == self.ticker:
            if not self.invested and self.bars == 0:
                signal = None