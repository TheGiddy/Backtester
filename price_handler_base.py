from abc import ABCMeta


class AbstractPriceHandler(object):
    """
    PriceHandler is a base class providing an interface for all subsequent (inherited) data handlers
    (both live and historic). The goal of a (derived) PriceHandler object is to output a set of TickEvents or BarEvents
    for each financial instrument and place them into an event queue. This will replicate how a live strategy would
    function as current tick/bar data would be streamed via a brokerage. Thus a historic and live system will be
    treated identically by the rest of the Backtester suite.
    """

    __metaclass__ = ABCMeta

    def unsubscribe_ticker(self, ticker):
        """
        Unsubscribes the price handler from a current ticker symbol

        :param ticker: The ticker to unsubscribe
        :return:
        """
        try:
            self.tickers.pop(ticker, None)
            self.tickers_data.pop(ticker, None)
        except KeyError:
            print('Could not unsubscribe ticker {0} as it was never subscribed'.format(ticker))

    def get_last_timestamp(self, ticker):
        """
        Returns the most recent actual timestamp for a given ticker

        :param ticker: The ticker to which the last time stamp should be returned for.
        :return:
        """
        if ticker in self.tickers:
            timestamp = self.tickers[ticker]['timestamp']
            return timestamp

        else:
            print('Timestamp for ticker {0} is not available from the {0}.'.format(ticker, self.__class__.__name__))
            return None


class AbstractBarPriceHandler(AbstractPriceHandler):
    def istick(self):
        return False

    def isbar(self):
        return True

    def _store_event(self, event):
        """
        Store price event for closing price and adjusted closing price
        """
        ticker = event.ticker
        self.tickers[ticker]['close'] = event.close_price
        #self.tickers[ticker]['adj_close'] = event.adj_close_price
        self.tickers[ticker]['timestamp'] = event.time

    def get_last_close(self, ticker):
        """
        Returns the most recent actual (unadjusted) closing price.
        """
        if ticker in self.tickers:
            close_price = self.tickers[ticker]['close']
            return close_price
        else:
            print('Close price for ticker {0} is not available from the Bar Handler'.format(ticker))
            return None

