from itertools import groupby

import numpy as np
import pandas as pd
from scipy.stats import linregress


def aggregate_returns(returns, convert_to):
    '''
    Aggregates returns by day, week, month, or year.

    :param returns:
    :param convert_to:
    :return:
    '''
    def cumulate_returns(x):
        return np.exp(np.log(1+x).cumsum())[-1] - 1

    if convert_to == 'weekly':
        return returns.groupby([lambda x: x.year,
                                lambda x: x.month,
                                lambda x: x.isocalendar()[1]]).apply(cumulate_returns)
    elif convert_to == 'monthly':
        return returns.groupby(
            [lambda x: x.year, lambda x: x.month]).apply(cumulate_returns)
    elif convert_to == 'yearly':
        return returns.groupby(
            [lambda x: x.year]).apply(cumulate_returns)
    else:
        ValueError('convert_to must be weekly, monthly or yearly')


def create_cagr(equity, periods=252):
    '''
    Calculates the Compound Annual Growth Rate (CAGR) for the portfolio, by determining the number of years and then
    creating a compound annualised rate based on the total return.

    :param equity: A pandas Series representing the equity curve.
    :param periods: Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    :return:
    '''
    years = len(equity) / float(periods)
    return (equity[-1] ** (1.0 / years)) - 1.0


def create_sharpe_ratio(returns, periods=252):
    '''
    Create the Sharpe ratio for the strategy, based on a benchmark of zero (i.e. no risk-free rate information).

    :param returns: A pandas Series representing period percentage returns.
    :param periods: Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    :return:
    '''
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)


def create_sortino_ratio(returns, periods=252):
    '''
    Create the Sortino ratio for the strategy, based on a benchmark of zero (i.e. no risk-free rate information).

    :param returns: A pandas Series representing period percentage returns.
    :param periods: Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    :return:
    '''
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns[returns < 0])


def create_drawdowns(returns):
    '''
    Calculate the largest peak-to-trough drawdown of the equity curve as well as the duration of the drawdown. Requires
    that the pnl_returns is a pandas Series.

    :param returns: drawdown, drawdown_max, duration
    :return:
    '''
    # Calculate the cumulative returns curve
    # and set up the High Water Mark
    idx = returns.index
    hwm = np.zeros(len(idx))

    # Create the high water mark
    for t in range(1, len(idx)):
        hwm[t] = max(hwm[t - 1], returns.ix[t])

    # Calculate the drawdown and duration statistics
    perf = pd.DataFrame(index=idx)
    perf["Drawdown"] = (hwm - returns) / hwm
    perf["Drawdown"].ix[0] = 0.0
    perf["DurationCheck"] = np.where(perf["Drawdown"] == 0, 0, 1)
    duration = max(
        sum(1 for i in g if i == 1)
        for k, g in groupby(perf["DurationCheck"])
    )
    return perf["Drawdown"], np.max(perf["Drawdown"]), duration


def rsquared(x, y):
    '''
    Return R^2 where x and y are array-like.

    :param x:
    :param y:
    :return:
    '''
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    return r_value**2
