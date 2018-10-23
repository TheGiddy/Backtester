import datetime
from event import SignalEvent, EventType
from strategy_base import AbstractStrategy
import queue
from trading_session import TradingSession
import settings


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
                signal = SignalEvent(self.ticker, 'BOT', suggested_quantity=self.base_quantity)
                self.events_queue.put(signal)
                self.invested = True
            self.bars = 1


def run(config, testing, tickers, filename):
    # Backtest information
    title = ['Test example on {0}'.format(tickers[0])]
    initial_quantity = 10000.0
    start_date = datetime.datetime(2016, 1, 1)
    end_date = datetime.datetime(2016, 12, 1)

    # Use the Buy and Hold Strategy
    events_queue = queue.Queue()
    strategy = TestStrategy(tickers[0], events_queue)

    # Set up the backtest
    backtest = TradingSession(config=config,
                              strategy=strategy,
                              tickers=tickers,
                              equity=initial_quantity,
                              start_date=start_date,
                              end_date=end_date,
                              events_queue=events_queue,
                              title=title)
    results = backtest.start_trading(testing=testing)
    return results


if __name__ == '__main__':
    # Configuration data
    testing = False
    config = settings.from_file(settings.DEFAULT_CONFIG_FILENAME, testing)
    tickers = ['APH.TO']
    filename = None
    run(config, testing, tickers, filename)