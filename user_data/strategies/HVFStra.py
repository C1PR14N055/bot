# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401

# --- Do not remove these libs ---
from datetime import timedelta
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
        "60": 0.1,
        "30": 0.1,
        "0": 0.1
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
        'buy': 'limit',
        'sell': 'limit',
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
                    'P1_NOT_NULL', 'P2_NOT_NULL', 'MinMax', 'MinMaxValues', 
        # create columns needed to get trade statistics
                    'entry_point', 'stop_loss', 'take_profit', 'risk_reward_ratio', 'stake_amount',
        # entry/exit trade
                    'buy', 'sell']] = np.nan


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

        # as we using iloc to indentify location
        # values will be different in other dataframes
        # in this dataframe we have column names = column number

        date_column = 0
        open_column = 1
        high_column = 2
        low_column  = 3
        risk_value  = 30

        # simplify the expresion
        minmax = dataframe[dataframe['MinMaxValues'].notnull()]

        # -8 is the numerical index for column MinMaxValues
        sl_values    = minmax.iloc[idx[0], -8].values
        entry_values = minmax.iloc[(idx[0] - 1), -8].values
        p1_values    = minmax.iloc[(idx[0] - 5), -8].values
        p2_values    = minmax.iloc[(idx[0] - 4), -8].values


        # populate trade statistics columns
        completed_pattern_time = minmax.iloc[idx[0], date_column] 
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'stop_loss'] = minmax.iloc[idx[0], low_column]
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'entry_point'] = minmax.iloc[(idx[0]-1), high_column].values
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'stake_amount'] = entry_values * (risk_value / (entry_values - sl_values))
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'take_profit'] = ((entry_values + sl_values) / 2) + (p1_values - p2_values)
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'risk_reward_ratio'] = (((entry_values + sl_values) / 2) + (p1_values - p2_values) - entry_values) / (entry_values - sl_values)


        dataframe.loc[

            (dataframe['date'] > completed_pattern_time) &
            (dataframe['date'] < completed_pattern_time + (completed_pattern_time - minmax.iloc[(idx[0] - 5), date_column])) &
            (dataframe['high'] = dataframe['entry_point']) &
            (dataframe['risk_reward_ratio'] > 3.5),

            'buy'] = 1
            
        return dataframe


    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
                # identify p1, p2
        dataframe.loc[:, ['P1', 'P2',
        # create columns needed to create intervals
                    'P1_NOT_NULL', 'P2_NOT_NULL', 'MinMax', 'MinMaxValues', 
        # create columns needed to get trade statistics
                    'entry_point', 'stop_loss', 'take_profit', 'risk_reward_ratio', 'stake_amount',
        # entry/exit trade
                    'buy', 'sell']] = np.nan


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

        # as we using iloc to indentify location
        # values will be different in other dataframes
        # in this dataframe we have column names = column number

        date_column = 0
        open_column = 1
        high_column = 2
        low_column  = 3
        risk_value  = 30

        # simplify the expresion
        minmax = dataframe[dataframe['MinMaxValues'].notnull()]

        # -8 is the numerical index for column MinMaxValues
        sl_values    = minmax.iloc[idx[0], -8].values
        entry_values = minmax.iloc[(idx[0] - 1), -8].values
        p1_values    = minmax.iloc[(idx[0] - 5), -8].values
        p2_values    = minmax.iloc[(idx[0] - 4), -8].values


        # populate trade statistics columns
        completed_pattern_time = minmax.iloc[idx[0], date_column] 
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'stop_loss'] = minmax.iloc[idx[0], low_column]
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'entry_point'] = minmax.iloc[(idx[0]-1), high_column].values
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'stake_amount'] = entry_values * (risk_value / (entry_values - sl_values))
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'take_profit'] = ((entry_values + sl_values) / 2) + (p1_values - p2_values)
        dataframe.loc[dataframe['date'].isin(completed_pattern_time), 'risk_reward_ratio'] = (((entry_values + sl_values) / 2) + (p1_values - p2_values) - entry_values) / (entry_values - sl_values)



        dataframe.loc[
            (dataframe['high'] = dataframe['take_profit']) |
            (dataframe['low']  = dataframe['stop_loss']), 
            # add new column with expiry date
            #(dataframe['date'] = )

            'sell'] = 1
            
        return dataframe
