import os
import pandas as pd
from price_handler_base import AbstractBarPriceHandler
from event import BarEvent
import queue
from price_parser import PriceParser


class JsonBarPriceHandler(AbstractBarPriceHandler):
    """
    JsonBarPriceHandler is designed to read JSON fiels of daily Open-High-Low-Close-Volume (OHLCV) data for each
    requested financial instrument and stream those to the provided events que as BarEvents.
    """

    def __init__(self, json_dir, events_que, init_tickers=None, start_date=None, end_date=None):
        """
        Takes the JSON directory, the events queue and a possible list of initial ticker symbols then creates
        an (optional) list of ticker subscriptions and associated prices.

        :param json_dir: Directory of JSON data files
        :param events_que: Que that holds all events
        :param init_tickers: Initial tickers
        :param start_date: Date to start retrieving bars from
        :param end_date: Date to stop retrieving bars from
        """
        self.json_dir = json_dir
        self.events_que = events_que
        self.continue_backtest = True
        self.tickers = {}
        self.tickers_data = {}
        if init_tickers is not None:
            for ticker in init_tickers:
                self.subscribe_ticker(ticker)
        self.start_date = start_date
        self.end_date = end_date
        self.bar_stream = self._merge_sort_ticker_data()

    def _open_ticker_price_json(self, ticker):
        """
        Opens the JSON files containing the equities ticks from the specified JSON data directory, converting them into
        them into a pandas DataFrame, stored in a dictionary.

        :param ticker: The ticker that should be opened.
        :return:
        """
        df = pd.DataFrame(data=None, index=None, columns=None)

        for year_d in os.listdir(self.json_dir):
            if os.path.isdir(os.path.join(self.json_dir, year_d)):
                cur_path = '{0}\\{1}\\{2}\\_{3}.json'.format(self.json_dir, year_d, ticker[0], ticker)
                cur_df = pd.read_json(cur_path, orient='records')
                df = df.append(cur_df)

        df['start'] = (pd.to_datetime(df['start']))
        df = df.reset_index(drop=True)
        df = df.drop_duplicates()
        df = df.set_index('start')
        self.tickers_data[ticker] = df
        self.tickers_data[ticker]['Ticker'] = ticker

    def _merge_sort_ticker_data(self):
        """
        Concatenates all of the separate equities DataFrames into a single DataFrame that is time ordered, allowing tick
        data events to be added to the queue in a chronological fashion. Note that this is an idealised situation,
        utilised solely for backtesting. In live trading ticks may arrive "out of order".
        """
        df = pd.concat(self.tickers_data.values()).sort_index()
        start = None
        end = None
        if self.start_date is not None:
            start = df.index.searchsorted(self.start_date)
        if self.end_date is not None:
            end = df.index.searchsorted(self.end_date)
        # This is added so that the ticker events are always deterministic, otherwise unit test values will differ
        df['colFromIndex'] = df.index
        df = df.sort_values(by=["colFromIndex", "Ticker"])
        if start is None and end is None:
            return df.iterrows()
        elif start is not None and end is None:
            return df.ix[start:].iterrows()
        elif start is None and end is not None:
            return df.ix[:end].iterrows()
        else:
            return df.ix[start:end].iterrows()

    def subscribe_ticker(self, ticker):
        """
        Subscribes the price handler to a new ticker symbol.

        :param ticker: The ticker to subscribe
        :return:
        """
        if ticker not in self.tickers:
            try:
                self._open_ticker_price_json(ticker)
                dft = self.tickers_data[ticker]
                row0 = dft.iloc[0]

                close = row0['close']

                ticker_prices = {
                    'close': close,
                    'timestamp': dft.index[0]
                }
                self.tickers[ticker] = ticker_prices
            except OSError:
                print(
                    'Could not subscribe ticker {0} as no data JSON found for pricing.'.format(ticker)
                )
        else:
            print('Could not subscribe ticker {0} as is already subscribed.'.format(ticker))



# evt_que = queue.Queue()
# x = JsonBarPriceHandler("E:\\OneDrive\\StockData\\EOD", evt_que, init_tickers=['APH.TO'])
# print(x)
# x.subscribe_ticker('WEED.TO')
# print(x.tickers)
# print(x.tickers_data)

    def _create_event(self, index, period, ticker, row):
        '''
        Obtain all elements of the bar from a row of dataframe and return a BarEvent

        :param index:
        :param period:
        :param ticker:
        :param row:
        :return:
        '''
        open_price = PriceParser.parse(row['open'])
        high_price = PriceParser.parse(row['high'])
        low_price = PriceParser.parse(row['low'])
        close_price = PriceParser.parse(row['close'])
        volume = int(row['volume'])
        bar_event = BarEvent(ticker, index, period, open_price, high_price, low_price, close_price, volume)

        return bar_event

    def _store_event(self, event):
        '''
        Store price event for closing price and adjusted closing price

        :param event:
        :return:
        '''
        ticker = event.ticker
        # If the calc_adj_returns flag is True, then calculate and store the full list of adjusted closing price
        # percentage returns in a list
        # TODO: Make this faster

        self.tickers[ticker]['close'] = event.close_price
        self.tickers[ticker]['timestamp'] = event.time

    def stream_next(self):
        '''
        Place the next bar event on the queue
        :return:
        '''

        try:
            index, row = next(self.bar_stream)
        except StopIteration:
            self.continue_backtest = False
            return

        # Obtain all elements of the bar from the dataframe
        ticker = row['ticker']
        period = 86400  # Seconds in a day

        # Create the tick event for the queue
        bar_event = self._create_event(index, period, ticker, row)

        # Store event
        self._store_event(bar_event)

        # Send event to queue
        self.events_que.put(bar_event)