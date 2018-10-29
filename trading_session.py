from datetime import datetime
import queue
from event import EventType
from price_handler_daily_bar import JsonBarPriceHandler
from price_parser import PriceParser
from portfolio import Portfolio
from portfolio_handler import PortfolioHandler
from risk_manager_example import ExampleRiskManager
from position_sizer_fixed import FixedPositionSizer



class TradingSession(object):
    """
    Enscapsulates the settings and components for carrying out either a backtest or live trading session.
    """
    def __init__(self,
                 config,
                 strategy,
                 tickers,
                 equity,
                 start_date,
                 end_date,
                 events_queue,
                 session_type='backtest',
                 end_session_time=None,
                 price_handler=None,
                 portfolio_handler=None,
                 compliance=None,
                 position_sizer=None,
                 execution_handler=None,
                 risk_manager=None,
                 statistics=None,
                 sentiment_handler=None,
                 title=None,
                 benchmark=None
                 ):
        self.equity = equity
        self.config = config
        self.strategy = strategy
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.events_queue = events_queue
        self.session_type = session_type
        self.end_session_time = end_session_time
        self.price_handler = price_handler
        self.portfolio_handler = portfolio_handler
        self.compliance = compliance
        self.execution_handler = execution_handler
        self.position_sizer = position_sizer
        self.risk_manager = risk_manager
        self.statistics = statistics
        self.sentiment_handler = sentiment_handler
        self.title = title
        self.benchmark = benchmark
        self.session_type = session_type
        self._config_session()
        self.cur_time = None

        if self.session_type == 'live':
            if self.end_session_time is None:
                raise Exception('Must specify an end_session_time when live trading')

    def _config_session(self):
        '''
        Initialises the necessary classes used within the session.
        :return:
        '''
        if self.price_handler is None and self.session_type == "backtest":
            self.price_handler = JsonBarPriceHandler(self.config.backtester.eod_json_data_dir,
                                                     self.events_queue,
                                                     self.tickers,
                                                     start_date=self.start_date,
                                                     end_date=self.end_date
                                                     )
        if self.portfolio_handler is None:
            self.portfolio_handler = PortfolioHandler(
                self.equity,
                self.events_queue,
                self.price_handler,
                self.position_sizer,
                self.risk_manager
            )

        if self.position_sizer is None:
            self.position_sizer = FixedPositionSizer()

        if self.risk_manager is None:
            self.risk_manager = ExampleRiskManager()

    def _continue_loop_condition(self):
        if self.session_type == 'backtest':
            return self.price_handler.continue_backtest
        else:
            return datetime.now() < self.end_session_time

    def _run_session(self):
        '''
        Carries out an infinite while loop that polls the events queue and directs each event to either the strategy
        component of the execution handler. The loop continue until the event queue has been emptied.
        '''
        if self.session_type == 'backtest':
            print('Running backtest...')
        else:
            print('Running realtime session until {0}'.format(self.end_session_time))

        while self._continue_loop_condition():
            try:
                event = self.events_queue.get(False)
                print(event)
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
