import pandas as pd
from backend.strategies.base import BaseStrategy
from backend.indicators.technical import calculate_atr


class BreakoutStrategy(BaseStrategy):
    name = "breakout"
    description = "Breakout Strategy - Enters on price breaking above/below support/resistance"

    def __init__(self, lookback: int = 20):
        self.lookback = lookback

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["highest"] = df["high"].rolling(window=self.lookback).max()
        df["lowest"] = df["low"].rolling(window=self.lookback).min()
        df["atr"] = calculate_atr(df["high"], df["low"], df["close"], 14)
        df["signal"] = 0
        df.loc[
            (df["close"] > df["highest"].shift(1)) & (df["volume"] > df["volume"].rolling(20).mean()),
            "signal",
        ] = 1
        df.loc[
            (df["close"] < df["lowest"].shift(1)) & (df["volume"] > df["volume"].rolling(20).mean()),
            "signal",
        ] = -1
        return df
