# user_data/strategies/ThreeDayTurn.py

import talib.abstract as ta
from freqtrade.strategy import IStrategy, IntParameter
from pandas import DataFrame


class DualMA(IStrategy):
    # --- 基础设置 ---
    timeframe = '1m'
    stoploss = -0.10
    minimal_roi = {}  # ← 不设止盈，完全靠趋势反转退出

    # --- 参数设置 ---
    ma_length = IntParameter(2, 6, default=3, space="buy")  # 3日均线

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 计算 3 日 SMA（技术平滑均线）
        dataframe['ma'] = ta.SMA(dataframe, timeperiod=self.ma_length.value)

        # 计算方向：1=上升，-1=下降，0=持平
        dataframe['ma_direction'] = 0
        dataframe.loc[dataframe['ma'] > dataframe['ma'].shift(1), 'ma_direction'] = 1
        dataframe.loc[dataframe['ma'] < dataframe['ma'].shift(1), 'ma_direction'] = -1

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 拐头向上：前一根是下降（-1），当前是上升（1）
        condition = (
                (dataframe['ma_direction'].shift(1) == -1) &
                (dataframe['ma_direction'] == 1)
        )
        dataframe.loc[condition, 'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # 拐头向下：前一根是上升（1），当前是下降（-1）
        condition = (
                (dataframe['ma_direction'].shift(1) == 1) &
                (dataframe['ma_direction'] == -1)
        )
        dataframe.loc[condition, 'exit_long'] = 1
        return dataframe
