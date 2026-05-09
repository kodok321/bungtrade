import pandas as pd
from backend.strategies.base import BaseStrategy
from backend.indicators.technical import calculate_rsi


class RSIStrategy(BaseStrategy):
    name = "rsi"
    description = "RSI Overbought/Oversold Strategy"

    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["rsi"] = calculate_rsi(df["close"], self.period)
        df["signal"] = 0
        df.loc[
            (df["rsi"] < self.oversold) & (df["rsi"].shift(1) >= self.oversold), "signal"
        ] = 1
        df.loc[
            (df["rsi"] > self.overbought) & (df["rsi"].shift(1) <= self.overbought), "signal"
        ] = -1
        return df
