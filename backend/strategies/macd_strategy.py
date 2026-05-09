import pandas as pd
from backend.strategies.base import BaseStrategy
from backend.indicators.technical import calculate_macd


class MACDStrategy(BaseStrategy):
    name = "macd"
    description = "MACD Crossover Strategy"

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        macd = calculate_macd(df["close"], self.fast, self.slow, self.signal_period)
        df["macd"] = macd["macd"]
        df["macd_signal"] = macd["signal"]
        df["macd_hist"] = macd["histogram"]
        df["signal"] = 0
        df.loc[
            (df["macd"] > df["macd_signal"]) & (df["macd"].shift(1) <= df["macd_signal"].shift(1)),
            "signal",
        ] = 1
        df.loc[
            (df["macd"] < df["macd_signal"]) & (df["macd"].shift(1) >= df["macd_signal"].shift(1)),
            "signal",
        ] = -1
        return df
