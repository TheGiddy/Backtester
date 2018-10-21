from datetime import datetime
import queue
from event import EventType
from price_handler_daily_bar import JsonBarPriceHandler
from price_parser import PriceParser


class TradingSession(object):
    """
    Enscapsulates the settings and components for carrying out either a backtest or live trading session.
    """
    def __init__(self,
                 tickers,
                 start_date,
                 end_date,
                 events_que,
                 session_type='backtest',
                 end_session_time=None,
                 price_handler=None):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.events_que = events_que
        self.session_type = session_type
        self.end_session_time = end_session_time
        self.price_handler = price_handler
        self._config_session()
        self.cur_time = None

        if self.session_type == 'live':
            if self.end_session_time is None:
                raise Exception('Must specify an end_session_time when live trading')

    def _config_session(self):
        """
        Initialises the necessary classes used within the session.
        :return:
        """

        pass

    def _continue_loop_condition(self):
        if self.session_type == 'backtest':
            return self.price_handler.continue_backtest
        else:
            return datetime.now() < self.end_session_time

    def _run_session(self):
        """
        Carries out an infinite while loop that polls the events queue and directs each event to either the strategy
        component of the execution handler. The loop continue until the event queue has been emptied.
        """
        if self.session_type == 'backtest':
            print('Running backtest...')
        else:
            print('Running realtime session until {0}'.format(self.end_session_time))

        while self._continue_loop_condition():
            try:
                event = self.events_que.get(False)
            except queue.Empty:
                self.price_handler.stream_next()
            else:
                if event is not None:
                    if event.type == EventType.TICK or event.type == EventType.BAR:
                        self.cur_time = event.time

    def start_trading(self, testing=False):
        """
        Runs either a backtest or live session, and outputs performance when complete.
        """
        self._run_session()