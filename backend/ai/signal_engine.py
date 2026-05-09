import pandas as pd
import numpy as np
from backend.exchange.binance_client import BinanceClient
from backend.indicators.technical import get_all_indicators, calculate_rsi, calculate_ema, calculate_atr


class AISignalEngine:
    def __init__(self):
        self.timeframes = ["15m", "1h", "4h"]

    async def generate_signal(self, symbol: str, timeframe: str = "1h") -> dict:
        client = BinanceClient()
        klines = await client.get_klines(symbol, timeframe, limit=200)

        df = pd.DataFrame(klines)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col])

        indicators = get_all_indicators(df)
        analysis = self._analyze(df, indicators)
        confidence = self._calculate_confidence(analysis)
        side = "BUY" if analysis["trend_score"] > 0 else "SELL"
        current_price = float(df["close"].iloc[-1])
        atr_val = float(indicators["atr"].iloc[-1]) if not pd.isna(indicators["atr"].iloc[-1]) else current_price * 0.02

        if side == "BUY":
            tp = round(current_price + atr_val * 2, 2)
            sl = round(current_price - atr_val * 1.5, 2)
        else:
            tp = round(current_price - atr_val * 2, 2)
            sl = round(current_price + atr_val * 1.5, 2)

        trend = "Bullish" if analysis["trend_score"] > 0 else "Bearish"

        return {
            "symbol": symbol,
            "side": side,
            "confidence": round(confidence, 1),
            "entry_price": current_price,
            "take_profit": tp,
            "stop_loss": sl,
            "trend": trend,
            "strategy": "AI Adaptive",
            "analysis": {
                "trend_score": analysis["trend_score"],
                "momentum_score": analysis["momentum_score"],
                "volatility_score": analysis["volatility_score"],
                "volume_score": analysis["volume_score"],
                "rsi": round(float(indicators["rsi"].iloc[-1]), 1) if not pd.isna(indicators["rsi"].iloc[-1]) else 50,
                "macd_histogram": round(float(indicators["macd_histogram"].iloc[-1]), 4) if not pd.isna(indicators["macd_histogram"].iloc[-1]) else 0,
                "atr": round(atr_val, 4),
            },
        }

    def _analyze(self, df: pd.DataFrame, indicators: dict) -> dict:
        close = df["close"]
        current = float(close.iloc[-1])

        trend_score = 0
        ema_9 = float(indicators["ema_9"].iloc[-1]) if not pd.isna(indicators["ema_9"].iloc[-1]) else current
        ema_21 = float(indicators["ema_21"].iloc[-1]) if not pd.isna(indicators["ema_21"].iloc[-1]) else current
        ema_50 = float(indicators["ema_50"].iloc[-1]) if not pd.isna(indicators["ema_50"].iloc[-1]) else current

        if current > ema_9:
            trend_score += 1
        if current > ema_21:
            trend_score += 1
        if current > ema_50:
            trend_score += 1
        if ema_9 > ema_21:
            trend_score += 1
        if ema_21 > ema_50:
            trend_score += 1

        if current < ema_9:
            trend_score -= 1
        if current < ema_21:
            trend_score -= 1
        if current < ema_50:
            trend_score -= 1

        rsi_val = float(indicators["rsi"].iloc[-1]) if not pd.isna(indicators["rsi"].iloc[-1]) else 50
        momentum_score = 0
        if rsi_val < 30:
            momentum_score = 2
        elif rsi_val < 45:
            momentum_score = 1
        elif rsi_val > 70:
            momentum_score = -2
        elif rsi_val > 55:
            momentum_score = -1

        macd_hist = float(indicators["macd_histogram"].iloc[-1]) if not pd.isna(indicators["macd_histogram"].iloc[-1]) else 0
        if macd_hist > 0:
            momentum_score += 1
        else:
            momentum_score -= 1

        atr_val = float(indicators["atr"].iloc[-1]) if not pd.isna(indicators["atr"].iloc[-1]) else 0
        volatility_score = 0
        atr_pct = (atr_val / current * 100) if current else 0
        if atr_pct < 1:
            volatility_score = 1
        elif atr_pct < 2:
            volatility_score = 0
        else:
            volatility_score = -1

        volume = df["volume"]
        vol_mean = float(volume.rolling(20).mean().iloc[-1]) if len(volume) >= 20 else float(volume.mean())
        vol_current = float(volume.iloc[-1])
        volume_score = 1 if vol_current > vol_mean else -1

        return {
            "trend_score": trend_score,
            "momentum_score": momentum_score,
            "volatility_score": volatility_score,
            "volume_score": volume_score,
        }

    def _calculate_confidence(self, analysis: dict) -> float:
        total = (
            abs(analysis["trend_score"]) * 3
            + abs(analysis["momentum_score"]) * 2
            + abs(analysis["volatility_score"])
            + abs(analysis["volume_score"])
        )
        max_possible = 5 * 3 + 3 * 2 + 1 + 1
        raw_score = total / max_possible * 100
        return min(max(raw_score, 15), 95)
