from abc import ABCMeta, abstractmethod


class AbstractPositionSizer(object):
    '''
    The AbstractPositionSizer abstract class modifies the quantity (or not) of any share transacted
    '''

    __metaclass__ =ABCMeta

    @abstractmethod
    def size_order(self, portfolio, initial_order):
        '''
        This TestPositionSizer object simply modifies the quantity to be 100 of any share transacted.
        :param portfolio:
        :param initial_order:
        :return:
        '''
        raise NotImplementedError('Should implement size_order()')