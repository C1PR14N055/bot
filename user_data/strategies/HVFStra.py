# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401

# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class HVFStra(IStrategy):
    """
    This is a strategy template to get you started.
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_buy_trend, populate_sell_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 2

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.10

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Optimal timeframe for the strategy.
    timeframe = '5m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = True
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Optional order type mapping.
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['sma50'] = ta.SMA(dataframe, timeperiod=50)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with buy column
        """
        # dataframe.loc[
        #     (
        #         (qtpylib.crossed_above(dataframe['rsi'], 30)) &  # Signal: RSI crosses above 30
        #         (dataframe['tema'] <= dataframe['bb_middleband']) &  # Guard: tema below BB middle
        #         (dataframe['tema'] > dataframe['tema'].shift(1)) &  # Guard: tema is raising
        #         (dataframe['volume'] > 0)  # Make sure Volume is not 0
        #     ),
        #     'buy'] = 1

        # 3

        # Add SMA column
        # dataframe.loc[:, 'sma'] = round(dataframe.close.rolling(window=60).mean(), 1)
        # dataframe.dropna(inplace=True)

        # Create SMA for high/low
        # dataframe.loc[:, 'high_sma'] = dataframe.high.rolling(window=50).mean()
        # dataframe.loc[:, 'low_sma'] = dataframe.low.rolling(window=50).mean()

        # Add P1...P6
        # dataframe.loc[:, ['PP1', 'PP2', 'PP3', 'PP4', 'PP5', 'PP6']] = 0
        dataframe.loc[:, ['P1', 'P2',
                          'P1_NOT_NULL', 'P2_NOT_NULL', 'MinMax', 'MinMaxValues', 'buy']
                      ] = np.nan

        # P1 is composed of any `high` above `SMA` at this momment
        dataframe.loc[:, 'P1'] = dataframe.P1.mask(
            dataframe['close'] > dataframe['sma50'], dataframe['high'])
        # P2 is composed of any `low` below `SMA` at this momment
        dataframe.loc[:, 'P2'] = dataframe.P2.mask(
            dataframe['close'] < dataframe['sma50'], dataframe['low'])

        # invert dataframeframe to search in chronological order
        # dataframe = dataframe[::-1]
        # dataframe = dataframe.reset_index()

        # convert str to date
        # dataframe['date'] = pd.to_datetime(dataframe['date'])

        # greater than the start date and smaller than the end date
        # mask = (dataframe['date'] > start_date) & (dataframe['date'] <= end_date)

        # copy to new df to get rid of warning, reset_index for further usage
        # dataframe = dataframe.loc[mask].copy().reset_index()

        # add 1 to col P1_NOT_NULL when hight above SMA
        dataframe.loc[:, 'P1_NOT_NULL'] = dataframe.P1_NOT_NULL.mask(
            dataframe['close'] > dataframe['sma50'], 1)

        # add 1 to col P2_NOT_NULL when low bellow SMA
        dataframe.loc[:, 'P2_NOT_NULL'] = dataframe.P2_NOT_NULL.mask(
            dataframe['close'] < dataframe['sma50'], 1)

        # null values in P1_NOT_NULL
        isnull_p1 = dataframe.loc[:, 'P1_NOT_NULL'].isnull()

        # null values in P2_NOT_NULL
        isnull_p2 = dataframe.loc[:, 'P2_NOT_NULL'].isnull()

        idxmax = dataframe.groupby(isnull_p1.cumsum()[~isnull_p1])['P1'].agg(['idxmax'])
        idxmin = dataframe.groupby(isnull_p2.cumsum()[~isnull_p2])['P2'].agg(['idxmin'])

        # populate MinMax column with min/max values of high and low
        dataframe.loc[idxmax['idxmax'], 'MinMax'] = 'max'
        dataframe.loc[idxmin['idxmin'], 'MinMax'] = 'min'

        dataframe.loc[:, 'MinMaxValues'] = dataframe.MinMaxValues.mask(
            dataframe['MinMax'] == 'max', dataframe['high'])
        dataframe.loc[:, 'MinMaxValues'] = dataframe.MinMaxValues.mask(
            dataframe['MinMax'] == 'min', dataframe['low']

        )

        """
		print('data with minmax values only')
		print(data[data['MinMax'].notnull()][['date', 'high', 'low',
		'sma', 'MinMaxValues', 'MinMax']])
		print('*' * 50)

		print("data filtered broader view")
		print(data.loc[:, ['date', 'high', 'P1', 'low', 'P2', 'close', 'sma', 'MinMaxValues', 'MinMax']])

		# index = 79 date = 2021-10-07 02:20:00 low = 430.0 sma = 430.440 MinMax = 430.0 min
		# TradingView MA50 has different values than sma
		# A StackOverflow post was saying that the difference may be becouse of the different starting time of calulating the mean()/MA60

		# In our current situatian the sma calculated with mean gives extra min/max points which are false pozitive signals
		# Comparing the first value of sma from the dataframe with the value at the same time in TradingView we have:
		# sma = 427.622 && TradigView MA50 = 430.4
		# In dataframe the price is above sma  (high = 430.0 > sma = 427.622)
		# In TradingView the price is beloe MA50 (low = 429.3 < MA50 = 430.4)
		"""

        p6 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues']
        p5 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(1)
        p4 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(2)
        p3 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(3)
        p2 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(4)
        p1 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(5)

        idx = np.where(
            # check fib level of p6 (stop loss)
            (p6 - p2 >= 0.382 * (p1 - p2)) &
            (p6 - p2 <= 0.500 * (p1 - p2)) &

            # check fib level of p5 (entry point)
            (p5 - p4 >= 0.50 * (p3 - p4)) &
            (p5 - p4 <= 0.61 * (p1 - p2)) &

            # check fib level of p4
            (p4 - p2 >= 0.10 * (p1 - p2)) &
            (p4 - p2 <= 0.33 * (p1 - p2)) &

            # check fib level of p3
            (p3 - p2 >= 0.786 * (p1 - p2)) &
            (p3 - p2 <= p1 - p2)
        )

        print('idx')
        print(idx)
        # idx values are index values from the slice (a DataFrame by itself) => data['MinMaxValues'].notnull() not from data DataFrame
        # get the time of idx ('date' values are global values present in both DataFrames)
        hvf_time = dataframe[dataframe['MinMaxValues'].notnull()].iloc[idx[0], 0]
        print('hvf_time')
        print(hvf_time)

        print('*' * 50)
        print(dataframe[dataframe['buy'].notnull()])
        print('*' * 50)

        dataframe.loc[dataframe['date'].isin(hvf_time), 'buy'] = 1
        # print('dataframe[dataframe[MinMaxValues].notnull()].iloc[idx[0], :]')
        # print(dataframe[dataframe['MinMaxValues'].notnull()].iloc[idx[0], :])
        # print('*' * 50)

        # print('dataframe.iloc[idx[0], :]')
        # print(dataframe.iloc[idx[0], :])
        # print('*' * 50)
        # print(idx)

        # start_date = '2021-08-13 21:13:00'
        # end_date = '2021-08-13 22:26:00'

        # greater than the start date and smaller than the end date
        # mask = (dataframe['date'] > start_date) & (dataframe['date'] <= end_date)

        # copy to new df to get rid of warning, reset_index for further usage
        # test_dataframe = dataframe.loc[mask].copy().reset_index()
        # test_dataframe.set_index(test_dataframe.date.values, drop=True, inplace=True)

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe
