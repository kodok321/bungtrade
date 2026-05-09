import pandas as pd
from backend.strategies.base import BaseStrategy
from backend.indicators.technical import calculate_ema


class EMACrossStrategy(BaseStrategy):
    name = "ema_cross"
    description = "EMA Crossover Strategy - Uses 9/21 EMA crossover for entry signals"

    def __init__(self, fast_period: int = 9, slow_period: int = 21):
        self.fast_period = fast_period
        self.slow_period = slow_period

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["ema_fast"] = calculate_ema(df["close"], self.fast_period)
        df["ema_slow"] = calculate_ema(df["close"], self.slow_period)
        df["signal"] = 0
        df.loc[
            (df["ema_fast"] > df["ema_slow"]) & (df["ema_fast"].shift(1) <= df["ema_slow"].shift(1)),
            "signal",
        ] = 1
        df.loc[
            (df["ema_fast"] < df["ema_slow"]) & (df["ema_fast"].shift(1) >= df["ema_slow"].shift(1)),
            "signal",
        ] = -1
        return df
