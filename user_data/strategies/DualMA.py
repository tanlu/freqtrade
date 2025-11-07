# user_data/strategies/FourBarMAConfirm.py

import talib.abstract as ta
from freqtrade.strategy import IStrategy, IntParameter
from pandas import DataFrame


class FourBarMAConfirm(IStrategy):
    # --- 基础设置 ---
    timeframe = '1m'
    stoploss = -0.10
    minimal_roi = {}  # ← 不设止盈，完全依赖趋势退出

    # --- 可调参数 ---
    fast_length = IntParameter(5, 20, default=10, space="buy")
    slow_length = IntParameter(20, 50, default=30, space="buy")
    confirm_bars = 4  # 连续确认K线数（固定为4）

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 计算快慢均线
        dataframe['fast_ma'] = ta.SMA(dataframe, timeperiod=self.fast_length.value)
        dataframe['slow_ma'] = ta.SMA(dataframe, timeperiod=self.slow_length.value)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 要求最近 confirm_bars 根K线都满足 fast_ma > slow_ma
        condition = True
        for i in range(self.confirm_bars):
            condition = condition & (dataframe['fast_ma'].shift(i) > dataframe['slow_ma'].shift(i))

        dataframe.loc[condition, 'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 要求最近 confirm_bars 根K线都满足 fast_ma < slow_ma
        condition = True
        for i in range(self.confirm_bars):
            condition = condition & (dataframe['fast_ma'].shift(i) < dataframe['slow_ma'].shift(i))

        dataframe.loc[condition, 'exit_long'] = 1
        return dataframe
