import pandas as pd
import numpy as np
from datetime import datetime
from backend.exchange.binance_client import BinanceClient
from backend.strategies.registry import get_strategy


class BacktestEngine:
    async def run(
        self,
        strategy: str,
        symbol: str,
        timeframe: str = "1h",
        start_date: str = "2024-01-01",
        end_date: str = "2024-12-31",
        initial_balance: float = 10000.0,
    ) -> dict:
        client = BinanceClient()
        klines = await client.get_klines(symbol, timeframe, limit=1000)

        df = pd.DataFrame(klines)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col])

        strat = get_strategy(strategy)
        df = strat.generate_signals(df)

        balance = initial_balance
        position = None
        trades_log = []
        equity_curve = [{"time": int(df["time"].iloc[0]), "balance": balance}]
        peak_balance = initial_balance

        for i in range(1, len(df)):
            row = df.iloc[i]
            signal = row.get("signal", 0)
            price = float(row["close"])

            if signal == 1 and position is None:
                qty = (balance * 0.95) / price
                position = {"side": "BUY", "entry": price, "qty": qty, "time": int(row["time"])}
            elif signal == -1 and position is not None and position["side"] == "BUY":
                pnl = (price - position["entry"]) * position["qty"]
                balance += pnl
                trades_log.append({
                    "entry": position["entry"],
                    "exit": price,
                    "side": position["side"],
                    "pnl": round(pnl, 2),
                    "entry_time": position["time"],
                    "exit_time": int(row["time"]),
                })
                position = None
            elif signal == -1 and position is None:
                qty = (balance * 0.95) / price
                position = {"side": "SELL", "entry": price, "qty": qty, "time": int(row["time"])}
            elif signal == 1 and position is not None and position["side"] == "SELL":
                pnl = (position["entry"] - price) * position["qty"]
                balance += pnl
                trades_log.append({
                    "entry": position["entry"],
                    "exit": price,
                    "side": position["side"],
                    "pnl": round(pnl, 2),
                    "entry_time": position["time"],
                    "exit_time": int(row["time"]),
                })
                position = None

            if balance > peak_balance:
                peak_balance = balance
            equity_curve.append({"time": int(row["time"]), "balance": round(balance, 2)})

        if position is not None:
            price = float(df["close"].iloc[-1])
            if position["side"] == "BUY":
                pnl = (price - position["entry"]) * position["qty"]
            else:
                pnl = (position["entry"] - price) * position["qty"]
            balance += pnl
            trades_log.append({
                "entry": position["entry"],
                "exit": price,
                "side": position["side"],
                "pnl": round(pnl, 2),
                "entry_time": position["time"],
                "exit_time": int(df["time"].iloc[-1]),
            })

        winning = [t for t in trades_log if t["pnl"] > 0]
        losing = [t for t in trades_log if t["pnl"] <= 0]
        total_trades = len(trades_log)
        winrate = (len(winning) / total_trades * 100) if total_trades > 0 else 0

        max_dd = 0
        peak = initial_balance
        for point in equity_curve:
            if point["balance"] > peak:
                peak = point["balance"]
            dd = (peak - point["balance"]) / peak * 100
            if dd > max_dd:
                max_dd = dd

        gross_profit = sum(t["pnl"] for t in winning) if winning else 0
        gross_loss = abs(sum(t["pnl"] for t in losing)) if losing else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        returns = []
        for i in range(1, len(equity_curve)):
            prev = equity_curve[i - 1]["balance"]
            curr = equity_curve[i]["balance"]
            if prev > 0:
                returns.append((curr - prev) / prev)
        avg_return = np.mean(returns) if returns else 0
        std_return = np.std(returns) if returns else 1
        sharpe = (avg_return / std_return * np.sqrt(252)) if std_return > 0 else 0

        return {
            "start_date": datetime.fromisoformat(start_date),
            "end_date": datetime.fromisoformat(end_date),
            "initial_balance": initial_balance,
            "final_balance": round(balance, 2),
            "total_trades": total_trades,
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "winrate": round(winrate, 1),
            "max_drawdown": round(max_dd, 2),
            "sharpe_ratio": round(sharpe, 2),
            "profit_factor": round(profit_factor, 2),
            "equity_curve": equity_curve,
            "monthly_returns": {},
            "trades_log": trades_log,
        }
