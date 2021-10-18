# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401

# --- Do not remove these libs ---
from datetime import timedelta
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from pandas.core.algorithms import isin

pd.options.display.max_rows = 300
pd.options.display.max_columns = 30

pd.options.display.precision = 8

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
        "60": 0.1,
        "30": 0.1,
        "0": 0.1
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.99

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Optimal timeframe for the strategy.
    timeframe = '1m'

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
        'buy': 'market',
        'sell': 'market',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
    #                     proposed_stake: float, min_stake: float, max_stake: float,
    #                     **kwargs) -> float:

    # dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
    # current_candle = dataframe.iloc[-1].squeeze()
    # # parameter to be set global and calculated at the begining of setting up the account
    # # it should be a procent of the account 
    # # custm_risk_amount should be a int value representing an amount 
    # # calculated as: procent_of_risk_adversion * account_balance
    # custm_risk_amount = 30

    # # p5 value should be extracted from the populate_buy_trend()
    # # p5 value is the value where we place the limit order 
    # # p5 it is the price that we buy the coin
    # custm_entry_price = p5 


    # # p6 value should be extracted from the populate_buy_trend()
    # custm_stop_loss_price = p6


    # # get the distance from entry untill stop_loss
    # # percentege_in_points aka pip (or satoshi in crypto)
    # custm_stop_loss_distance = custm_entry_price - custm_stop_loss_price

    # # determine the quantity to be bought based on custm_stop_loss_distance
    # custm_qty = custm_risk_amount / custm_stop_loss_distance

    # custm_stake_amount = custm_entry_price * custm_qty

    # return custm_stake_amount

    # if current_candle['fastk_rsi_1h'] > current_candle['fastd_rsi_1h']:
    #     if self.config['stake_amount'] == 'unlimited':
    #         # Use entire available wallet during favorable conditions when in compounding mode.
    #         return max_stake
    #     else:
    #         # Compound profits during favorable conditions instead of using a static stake.
    #         return self.wallets.get_total_stake_amount() / self.config['max_open_trades']

    # # Use default stake amount.
    # return proposed_stake


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

        # identify p1, p2
        dataframe.loc[:, ['P1', 'P2', 
        # create columns needed to create intervals
                    'P1_NOT_NULL', 'P2_NOT_NULL', 'time_dif', 'expiry', 'MinMax', 'MinMaxValues', 
        # create columns needed to get trade statistics
                    'entry_point', 'stop_loss', 'take_profit', 'risk_reward_ratio', 'stake_amount']] = np.nan
        # entry/exit trade


        # P1 is composed of any `high` above `SMA` at this momment
        dataframe.loc[:, 'P1'] = dataframe.P1.mask(
            dataframe['close'] > dataframe['sma50'], dataframe['high'])
        # P2 is composed of any `low` below `SMA` at this momment
        dataframe.loc[:, 'P2'] = dataframe.P2.mask(
            dataframe['close'] < dataframe['sma50'], dataframe['low'])


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

        p6 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].copy()
        p5 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(1).copy()
        p4 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(2).copy()
        p3 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(3).copy()
        p2 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(4).copy()
        p1 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(5).copy()

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

        # as we using iloc to indentify location
        # values will be different in other dataframes
        # in this dataframe we have column names = column number
        date_column = 0
        open_column = 1
        high_column = 2
        low_column  = 3
        risk_value  = 30

        # simplify the expresion
        minmax = dataframe[dataframe['MinMaxValues'].notnull()].copy()

        # -6 is the numerical index for column MinMaxValues
        sl_values    = minmax.iloc[idx[0], -6].values.copy()
        entry_values = minmax.iloc[(idx[0] - 1), -6].values.copy()
        p1_values    = minmax.iloc[(idx[0] - 5), -6].values.copy()
        p2_values    = minmax.iloc[(idx[0] - 4), -6].values.copy()

        # populate trade statistics columns
        completed_pattern_time = minmax.iloc[idx[0], date_column].copy()
        p1_time = minmax.iloc[(idx[0] - 5), date_column]

        diff = (completed_pattern_time.values - p1_time.values).astype('timedelta64[m]')


        
        # print('time difference')
        # print(diff)
        # print('*' * 50)


        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'stop_loss'] = minmax.iloc[idx[0], low_column].copy()
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'entry_point'] = minmax.iloc[(idx[0]-1), high_column].values.copy()
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'stake_amount'] = entry_values * (risk_value / (entry_values - sl_values)).copy()
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'take_profit'] = ((entry_values + sl_values) / 2) + (p1_values - p2_values).copy()
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'risk_reward_ratio'] = (((entry_values + sl_values) / 2) + (p1_values - p2_values) - entry_values) / (entry_values - sl_values).copy()
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'time_dif'] = (minmax.iloc[idx[0], date_column].values - minmax.iloc[(idx[0] - 5), date_column].values).astype('timedelta64[m]')
        # dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'expiry'] = dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'date'] + dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'time_dif']
        # dataframe.loc[dataframe['time_dif'].notnull(), 'time_dif']astype(int)
     
        # print(dataframe[dataframe['time_dif'].notnull()])
        # print('*' * 50)

        # get the index in dataframe where pattern was completed
        index_location = np.where(dataframe['date'].isin(completed_pattern_time))
        # convert the result to list to be passed as numerical index 
        lst_idx = [x for x in index_location[0]]




        # get the index of p1 & p6
        p1_index = np.where(dataframe['MinMaxValues'].equals(p1_values))
        # p6_index = np.where(dataframe['low'].equals(p6values))


        # number of columns to fill with trade statistics
        time_out = 50
        # fill entry_point values with a limited number of rows to initialize the trade
        dataframe.loc[:, 'entry_point'].fillna(method='ffill', limit = time_out, inplace=True)
        dataframe.loc[:, 'risk_reward_ratio'].fillna(method='ffill', limit = time_out, inplace=True)
        dataframe.loc[:, 'stop_loss'].fillna(method='ffill', limit = time_out, inplace=True)
        dataframe.loc[:, 'take_profit'].fillna(method='ffill', limit = time_out, inplace=True)
        dataframe.loc[:, 'time_dif'].fillna(method='ffill', limit = time_out, inplace=True)
        # dataframe.loc[:, 'expiry'].fillna(method='ffill', limit = time_out, inplace=True)



        dataframe.loc[
            (
                (dataframe['high'].shift() < dataframe['entry_point'].shift()) &
                (dataframe['high'] >= dataframe['entry_point']) &
                (dataframe.iloc[lst_idx[-1]:-1, low_column].min() > dataframe['low'])&
                (dataframe['risk_reward_ratio'] > 5)
            ),
            'buy'] = 1


        # print('lst_idx loop')
        # print(lst_idx[x] for x in range(len(lst_idx)))
        # # print(type(lst_idx))
        # print('*' * 50)
        # print('lst_idx[0]')
        # print(lst_idx[0])
        # print('*' * 50)

        expiry_times = dataframe.loc[dataframe['buy'] == 1,'date'] + dataframe.loc[dataframe['buy'] == 1,'time_dif']

        dataframe.loc[
            (
                (dataframe['expiry'].isnull()) &
                (dataframe['date'].isin(expiry_times))
            ),
            'expiry' ] = 1


        dataframe.loc[
            (
            
                (dataframe['expiry'] == 1) |
                (dataframe['high'] >= dataframe['take_profit']) |
                (dataframe['low']  <= dataframe['stop_loss'])
                # add new column with expiry date
                #(dataframe['date'] = )
            ),
            'sell'] = 1
        # print(dataframe[(dataframe['take_profit'].notnull()) & (dataframe['risk_reward_ratio'] > 3)])
        # print('time diff column')
        # dataframe.loc[dataframe['buy'] == 1, 'expiry'] = dataframe[dataframe['buy'] == 1]['date'] + dataframe[dataframe['buy'] == 1]['time_dif']

        # print(dataframe[dataframe['buy'] == 1, 'time_dif']['time_dif'].astype(int))
        # print(type(dataframe[dataframe['buy'] == 1, 'time_dif'].values.astype(int)))

        # print('*' * 50)
        # dataframe.loc[:, 'take_profit'].fillna(method='ffill',
        # limit = dataframe.loc[dataframe['buy'] == 1, 'time_diff'].astype(int),
        # inplace=True)


        # p1_time = minmax.iloc[(idx[0] - 5), date_column]
        # diff = completed_pattern_time - p1_time

        # print('completed_pattern_time')
        # print(completed_pattern_time.iloc[-1])
        # print(completed_pattern_time)
        # print('*' * 50)

        # print('p1_time')
        # print(minmax.iloc[(idx[0] - 5), date_column])
        # print('*' * 50)

        # print('entry_point')
        # print(dataframe[dataframe['entry_point'].notnull()]['date'])  
        # print(type(dataframe[dataframe['entry_point'].notnull()]['date']))  
        # print('*' * 50)
        return dataframe


    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # print('entry_point')
        # print(dataframe[dataframe['entry_point'].notnull()])  
        # print('*' * 50)


        #         # identify p1, p2
        # dataframe.loc[:, ['P1', 'P2',
        # # create columns needed to create intervals
        #             'P1_NOT_NULL', 'P2_NOT_NULL', 'MinMax', 'MinMaxValues', 
        # # create columns needed to get trade statistics
        #             'entry_point', 'stop_loss', 'take_profit', 'risk_reward_ratio', 'stake_amount',
        # # entry/exit trade
        #             'buy', 'sell']] = np.nan


        # # P1 is composed of any `high` above `SMA` at this momment
        # dataframe.loc[:, 'P1'] = dataframe.P1.mask(
        #     dataframe['close'] > dataframe['sma50'], dataframe['high'])
        # # P2 is composed of any `low` below `SMA` at this momment
        # dataframe.loc[:, 'P2'] = dataframe.P2.mask(
        #     dataframe['close'] < dataframe['sma50'], dataframe['low'])


        # # add 1 to col P1_NOT_NULL when hight above SMA
        # dataframe.loc[:, 'P1_NOT_NULL'] = dataframe.P1_NOT_NULL.mask(
        #     dataframe['close'] > dataframe['sma50'], 1)

        # # add 1 to col P2_NOT_NULL when low bellow SMA
        # dataframe.loc[:, 'P2_NOT_NULL'] = dataframe.P2_NOT_NULL.mask(
        #     dataframe['close'] < dataframe['sma50'], 1)

        # # null values in P1_NOT_NULL
        # isnull_p1 = dataframe.loc[:, 'P1_NOT_NULL'].isnull()

        # # null values in P2_NOT_NULL
        # isnull_p2 = dataframe.loc[:, 'P2_NOT_NULL'].isnull()

        # idxmax = dataframe.groupby(isnull_p1.cumsum()[~isnull_p1])['P1'].agg(['idxmax'])
        # idxmin = dataframe.groupby(isnull_p2.cumsum()[~isnull_p2])['P2'].agg(['idxmin'])

        # # populate MinMax column with min/max values of high and low
        # dataframe.loc[idxmax['idxmax'], 'MinMax'] = 'max'
        # dataframe.loc[idxmin['idxmin'], 'MinMax'] = 'min'

        # dataframe.loc[:, 'MinMaxValues'] = dataframe.MinMaxValues.mask(
        #     dataframe['MinMax'] == 'max', dataframe['high'])
        # dataframe.loc[:, 'MinMaxValues'] = dataframe.MinMaxValues.mask(
        #     dataframe['MinMax'] == 'min', dataframe['low']

        # )

        # p6 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues']
        # p5 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(1)
        # p4 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(2)
        # p3 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(3)
        # p2 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(4)
        # p1 = dataframe[dataframe['MinMaxValues'].notnull()]['MinMaxValues'].shift(5)

        # idx = np.where(
        #     # check fib level of p6 (stop loss)
        #     (p6 - p2 >= 0.382 * (p1 - p2)) &
        #     (p6 - p2 <= 0.500 * (p1 - p2)) &

        #     # check fib level of p5 (entry point)
        #     (p5 - p4 >= 0.50 * (p3 - p4)) &
        #     (p5 - p4 <= 0.61 * (p1 - p2)) &

        #     # check fib level of p4
        #     (p4 - p2 >= 0.10 * (p1 - p2)) &
        #     (p4 - p2 <= 0.33 * (p1 - p2)) &

        #     # check fib level of p3
        #     (p3 - p2 >= 0.786 * (p1 - p2)) &
        #     (p3 - p2 <= p1 - p2)
        # )

        # # as we using iloc to indentify location
        # # values will be different in other dataframes
        # # in this dataframe we have column names = column number

        # date_column = 0
        # open_column = 1
        # high_column = 2
        # low_column  = 3
        # risk_value  = 30

        # # simplify the expresion
        # minmax = dataframe[dataframe['MinMaxValues'].notnull()].copy()

        # # -6 is the numerical index for column MinMaxValues
        # sl_values    = minmax.iloc[idx[0], -6].values
        # entry_values = minmax.iloc[(idx[0] - 1), -6].values
        # p1_values    = minmax.iloc[(idx[0] - 5), -6].values
        # p2_values    = minmax.iloc[(idx[0] - 4), -6].values

        # # populate trade statistics columns
        # completed_pattern_time = minmax.iloc[idx[0], date_column] 

        # dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'stop_loss'] = minmax.iloc[idx[0], low_column]
        # dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'entry_point'] = minmax.iloc[(idx[0]-1), high_column].values
        # dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'stake_amount'] = entry_values * (risk_value / (entry_values - sl_values))
        # dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'take_profit'] = ((entry_values + sl_values) / 2) + (p1_values - p2_values)
        # dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'risk_reward_ratio'] = (((entry_values + sl_values) / 2) + (p1_values - p2_values) - entry_values) / (entry_values - sl_values)

        # # number of columns to fill with trade statistics
        # time_out = 30
        # # fill more columns with trade statistics
        # dataframe.loc[:, 'stop_loss'].fillna(method='ffill', limit = time_out, inplace=True)
        # dataframe.loc[:, 'take_profit'].fillna(method='ffill', limit = time_out, inplace=True)


        # dataframe.loc[
        #     (dataframe['high'] == dataframe['take_profit']) |
        #     (dataframe['low']  == dataframe['stop_loss']), 
        #     # add new column with expiry date
        #     #(dataframe['date'] = )

        #     'sell'] = 1

        # print('sell_signal')
        # print(dataframe[dataframe['sell'].notnull()])    
        # print('*' * 50) 

        return dataframe
