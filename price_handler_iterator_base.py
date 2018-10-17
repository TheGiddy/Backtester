from price_parser import PriceParser
from event import BarEvent
from exception import EmptyBarEvent


class AbstractPriceEventIterator(object):
    def __iter__(self):
        return self

    def next(self):
        return self.__next__()


class AbstractBarEventIterator(AbstractPriceEventIterator):
    def _create_event(self, index, period, ticker, row):
        """
        Obtain all elements of the bar from a row of dataframe and return a BarEvent
        """
        try:
            open_price = PriceParser.parse(row['open'])
            high_price = PriceParser.parse(row['high'])
            low_price = PriceParser.parse(row['low'])
            close_price = PriceParser.parse(row['close'])
            volume = PriceParser.parse(row['volume'])

            # Create the bar event for the queue
            bev = BarEvent(ticker, index, period, open_price, high_price, low_price, close_price, volume)

        except ValueError:
            raise EmptyBarEvent('row {0} {1} {2} {3} can\'t be convert to BarEvent'.format(index, period, ticker, row))
