import pandas as pd
from backend.strategies.base import BaseStrategy
from backend.indicators.technical import calculate_ema, calculate_rsi, calculate_atr


class ScalpingStrategy(BaseStrategy):
    name = "scalping"
    description = "Scalping Strategy - Quick entries with tight stops using EMA + RSI + ATR"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["ema_5"] = calculate_ema(df["close"], 5)
        df["ema_13"] = calculate_ema(df["close"], 13)
        df["rsi"] = calculate_rsi(df["close"], 7)
        df["atr"] = calculate_atr(df["high"], df["low"], df["close"], 10)
        df["signal"] = 0
        buy_cond = (
            (df["ema_5"] > df["ema_13"])
            & (df["rsi"] > 40)
            & (df["rsi"] < 65)
            & (df["close"] > df["ema_5"])
        )
        sell_cond = (
            (df["ema_5"] < df["ema_13"])
            & (df["rsi"] < 60)
            & (df["rsi"] > 35)
            & (df["close"] < df["ema_5"])
        )
        df.loc[buy_cond & ~buy_cond.shift(1).fillna(False), "signal"] = 1
        df.loc[sell_cond & ~sell_cond.shift(1).fillna(False), "signal"] = -1
        return df
