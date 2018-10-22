from enum import Enum


EventType = Enum("EventType", "TICK BAR SIGNAL ORDER FILL SENTIMENT")


class Event(object):
    """
        Event is base class providing an interface for all subsequent
        (inherited) events, that will trigger further events in the
        trading infrastructure.
    """
    @property
    def typename(self):
        return self.type.name


class BarEvent(Event):
    """
        Handles the event of receiving a new market
        open-high-low-close-volume bar, as would be generated
        via common data providers such as Yahoo Finance.
    """

    def __init__(self,
                 ticker,
                 time,
                 period,
                 open_price,
                 high_price,
                 low_price,
                 close_price,
                 volume,
                 adj_close_price=None):
        """
        Initialises the BarEvent

        :param ticker: The ticker symbol, e.g. 'AAPL'
        :param time: The timestamp of the bar
        :param period: The time period cover by the bar in seconds
        :param open_price: The unadjusted opening price of the bar
        :param high_price: The unadjusted high price of the bar
        :param low_price: The unadjusted low price of the bar
        :param close_price: The unadjusted close price of the bar
        :param volume: The volume of trading within the bar
        :param adj_close_price: The vendor adjusted closing price (e.g. back-adjustment) of the bar
        """

        self.type = EventType.BAR
        self.ticker = ticker
        self.time = time
        self.period = period
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.volume = volume
        self.adj_close_price = adj_close_price
        self.period_readable = self._readable_period()

    def _readable_period(self):
        """
        Creates a human-readable period from the number
        of seconds specified for 'period'.
        For instance, converts:
        * 1 -> '1sec'
        * 5 -> '5secs'
        * 60 -> '1min'
        * 300 -> '5min'
        If no period is found in the lookup table, the human
        readable period is simply passed through from period,
        in seconds.

        :return: String containing readable format
        """

        lut = {
            1: "1sec",
            5: "5sec",
            10: "10sec",
            15: "15sec",
            30: "30sec",
            60: "1min",
            300: "5min",
            600: "10min",
            900: "15min",
            1800: "30min",
            3600: "1hr",
            86400: "1day",
            604800: "1wk",
        }
        if self.period in lut:
            return lut[self.period]
        else:
            return "%ssec" % str(self.period)

    def __str__(self):
        format_str = "Type: %s, Ticker: %s, Time: %s, Period: %s, " \
                     "Open: %s, High: %s, Low: %s, Close: %s, " \
                     "Adj Close: %s, Volume: %s" % (
                         str(self.type), str(self.ticker), str(self.time),
                         str(self.period_readable), str(self.open_price),
                         str(self.high_price), str(self.low_price),
                         str(self.close_price), str(self.adj_close_price),
                         str(self.volume)
                     )
        return format_str

    def __repr__(self):
        return str(self)


class SignalEvent(Event):
    '''
    Handles the event of sending a Signal from a Strategy object. This is received by a Portfolio object and acted upon.
    '''
    def __init__(self, ticker, action, suggested_quantity=None):
        '''
        Initialises the SignalEvent.

        :param ticker: The ticker symbol, e.g. 'AAPL'
        :param action: 'BOT' (for long) or 'SLD' (for short)
        :param suggested_quantity: Optional positively valued integer representing a suggested absolute quantity of
                    units of an asset to transact in, which is used by the PositionSizer and RiskManager.
        '''
        self.type = EventType.SIGNAL
        self.ticker = ticker
        self.action = action
        self.suggested_quantity = suggested_quantity


class OrderEvent(Event):
    '''
    Handles the event of sending an Order to an execution system. The order contains a ticker (e.g. GOOG), action
    (BOT or SLD) and quantity.
    '''
    def __init__(self, ticker, action, quantity):
        '''
        Initialises the OrderEvent

        :param ticker: The ticker symbol, e.g. 'AAPL'
        :param action: 'BOT' (for long) or 'SLD' (for short).
        :param quantity: The quantity of shares to transact.
        '''
        self.type = EventType.ORDER
        self.ticker = ticker
        self.action = action
        self.quantity = quantity

    def print_order(self):
        '''
        Outputs the values within the OrderEvent.
        :return:
        '''
        print('Order: Ticker={0}, Action={1}, Quantity={2}'.format(self.ticker, self.action, self.quantity))


class FillEvent(Event):
    '''
    Encapsulates the notion of a filled order, as returned from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores the commission of the trade from the brokerage.

    TODO: Currently does not support filling positions at different prices. This will be simulated by averaging
    the cost.
    '''

    def __init__(self, timestamp, ticker, action, quantity, exchange, price, commission):
        '''

        :param timestamp: The timestamp when the order was filled.
        :param ticker: The ticker symbol, e.g. 'GOOG'.
        :param action: 'BOT' (for long) or 'SLD' (for short).
        :param quantity: The filled quantity.
        :param exchange: The exchange where the order was filled.
        :param price: The price at which the trade was filled
        :param commission: The brokerage commission for carrying out the trade.
        '''
        self.type = EventType.FILL
        self.timestamp = timestamp
        self.ticker = ticker
        self.action = action
        self.quantity = quantity
        self.exchange = exchange
        self.price = price
        self.commission = commission
