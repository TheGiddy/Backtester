import settings
import pandas as pd


class EquityHandler(object):
    def __init__(self, listingexchange=None, volumemin=500000):
        '''
        Initialise an EquityHandler object

        :param listingExchange: A list containing the exchanges to be queried
        '''
        self.listingExchange = listingexchange

    def get_symbols(self):
        '''
        Gets and returns all symbols that are apart of the requested exchange(s)

        :return:
        '''
        testing = False
        config = settings.from_file(settings.DEFAULT_CONFIG_FILENAME, testing)
        listing_file = config.backtester.listings_file
        listings = pd.read_json(listing_file, orient='index')

        if self.listingExchange is None:
            return listings.index.values.tolist()
        else:
            subset = listings[listings['listingExchange'].isin(self.listingExchange)]
            if subset.empty:
                print('There are no symbols listed for exchange {0}'.format(self.listingExchange))
                return None
            else:
                return subset.index.values.tolist()
