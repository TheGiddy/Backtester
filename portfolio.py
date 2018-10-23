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
            pt = self.positions[ticker]
            