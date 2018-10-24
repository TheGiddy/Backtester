from position import Position


class Portfolio(object):
    def __init__(self, price_handler, cash):
        '''
        On creation, the Portfolio object contains no positions and all values are "reset" to the initial cash, with
        no PnL - realised or unrealised.

        Note that realised_pnl is the running tally pnl from closed positions (closed_pnl), as well as realised_pnl
        from currently open positions.

        :param price_handler:
        :param cash:
        '''
        self.price_handler = price_handler
        self.init_cash = cash
        self.equity = cash
        self.cur_cash = cash
        self.positions = {}
        self.closed_positions = []
        self.realised_pnl = 0

    def _update_portfolio(self):
        '''
        Updates the value of all positions that are currently open.

        Value of closed positions is tallied as self.realised_pnl.
        :return:
        '''
        self.unrealised_pnl = 0
        self.equity = self.realised_pnl
        self.equity += self.init_cash

        for ticker in self.positions:
            position = self.positions[ticker]
            if self.price_handler.istick():
                bid, ask = self.price_handler.get_best_bid_ask(ticker)
            else:
                close_price = self.price_handler.get_last_close(ticker)
                bid = close_price
                ask = close_price
            position.update_market_value(bid, ask)
            self.unrealised_pnl += position.unrealised_pnl
            self.equity += (position.market_value - position.cost_basis + position.realised_pnl)

    def _add_position(self, action, ticker, quantity, price, commission):
        '''
        Adds a new Position object to the Portfolio. This requires getting the best bid/ask price from the price
        handler in order to calculate a reasonable "market value". Once the Position is added, the Portfolio values
        are updated.

        :param action:
        :param ticker:
        :param quantity:
        :param price:
        :param commission:
        :return:
        '''
        if ticker not in self.positions:
            if self.price_handler.istick():
                bid, ask = self.price_handler.get_best_bid_ask(ticker)
            else:
                close_price = self.price_handler.get_last_close(ticker)
                bid = close_price
                ask = close_price
            position = Position(action, ticker, quantity, price, commission, bid, ask)
            self.positions[ticker] = position
            self._update_portfolio()
        else:
            print('Ticker {0} is already in the positions list. Could not add a new position'.format(ticker))

    def _modify_position(self, action, ticker, quantity, price, commission):
        '''
        Modifies a current Position object to the Portfolio. This requires getting the best bid/ask price from the
        price handler in order to calculate a reasonable "market value". Once the Position is modified, the Portfolio
        values are updated.

        :param action:
        :param ticker:
        :param quantity:
        :param price:
        :param commission:
        :return:
        '''
        if ticker in self.positions:
            self.positions[ticker].transact_shares(action, quantity, price, commission)
            if self.price_handler.is_tick():
                bid, ask = self.price_handler.get_best_bid_ask(ticker)
            else:
                close_price = self.price_handler.get_last_close(ticker)
                bid = close_price
                ask = close_price
            self.positions[ticker].update_market_value(bid, ask)

            if self.positions[ticker].quantity == 0:
                closed = self.positions.pop(ticker)
                self.realised_pnl += closed.realised_pnl
                self.closed_positions.append(closed)
            self._update_portfolio()
        else:
            print('Ticker {0} not in the current position list. Could not modify a current position.'.format(ticker))

    def transact_position(self, action, ticker, quantity, price, commission):
        '''
        Handles any new position or modification to a current position, by calling the respective _add_position and
        _modify_position methods. Hence, this single method will be called by the PortfolioHandler to update the
        Portfolio itself.


        :param action: The position action 'BOT' or 'SLD'
        :param ticker: The ticker used
        :param quantity: The amount of shares
        :param price: The price
        :param commission: How much commission the brokerage charges
        :return:
        '''

        if action == 'BOT':
            self.cur_cash -= ((quantity * price) + commission)
        elif action == 'SLD':
            self.cur_cash += ((quantity * price) - commission)

        if ticker not in self.positions:
            self._add_position(action, ticker, quantity, price, commission)
        else:
            self._modify_position(action, ticker, quantity, price, commission)