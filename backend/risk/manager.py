from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional


@dataclass
class RiskConfig:
    risk_per_trade: float = 2.0
    max_daily_loss: float = 5.0
    max_drawdown: float = 10.0
    max_concurrent_trades: int = 5
    position_sizing_method: str = "fixed_percent"
    emergency_stop: bool = False


class RiskManager:
    def __init__(self, config: Optional[RiskConfig] = None):
        self.config = config or RiskConfig()
        self.daily_pnl: float = 0.0
        self.peak_balance: float = 0.0
        self.current_balance: float = 0.0
        self.open_positions: int = 0
        self.daily_reset: Optional[datetime] = None
        self.is_trading_stopped: bool = False

    def update_balance(self, balance: float):
        self.current_balance = balance
        if balance > self.peak_balance:
            self.peak_balance = balance

    def can_open_trade(self) -> tuple[bool, str]:
        self._check_daily_reset()

        if self.config.emergency_stop or self.is_trading_stopped:
            return False, "Trading is stopped (emergency or daily limit)"

        if self.open_positions >= self.config.max_concurrent_trades:
            return False, f"Max concurrent trades reached ({self.config.max_concurrent_trades})"

        daily_loss_pct = abs(self.daily_pnl / self.current_balance * 100) if self.current_balance else 0
        if self.daily_pnl < 0 and daily_loss_pct >= self.config.max_daily_loss:
            self.is_trading_stopped = True
            return False, f"Max daily loss reached ({self.config.max_daily_loss}%)"

        drawdown = self._calculate_drawdown()
        if drawdown >= self.config.max_drawdown:
            self.is_trading_stopped = True
            return False, f"Max drawdown reached ({self.config.max_drawdown}%)"

        return True, "OK"

    def calculate_position_size(
        self, entry_price: float, stop_loss: float, balance: Optional[float] = None
    ) -> float:
        bal = balance or self.current_balance
        risk_amount = bal * (self.config.risk_per_trade / 100)
        price_diff = abs(entry_price - stop_loss)
        if price_diff == 0:
            return 0
        return round(risk_amount / price_diff, 6)

    def record_trade_result(self, pnl: float):
        self.daily_pnl += pnl
        self.current_balance += pnl
        if self.current_balance > self.peak_balance:
            self.peak_balance = self.current_balance

    def _calculate_drawdown(self) -> float:
        if self.peak_balance == 0:
            return 0
        return (self.peak_balance - self.current_balance) / self.peak_balance * 100

    def _check_daily_reset(self):
        now = datetime.now(timezone.utc)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if self.daily_reset is None or self.daily_reset < today:
            self.daily_pnl = 0.0
            self.is_trading_stopped = False
            self.daily_reset = today

    def emergency_close_all(self):
        self.config.emergency_stop = True
        self.is_trading_stopped = True

    def resume_trading(self):
        self.config.emergency_stop = False
        self.is_trading_stopped = False

    def get_status(self) -> dict:
        return {
            "is_trading_stopped": self.is_trading_stopped,
            "emergency_stop": self.config.emergency_stop,
            "daily_pnl": round(self.daily_pnl, 2),
            "current_balance": round(self.current_balance, 2),
            "peak_balance": round(self.peak_balance, 2),
            "drawdown": round(self._calculate_drawdown(), 2),
            "open_positions": self.open_positions,
            "max_concurrent": self.config.max_concurrent_trades,
            "risk_per_trade": self.config.risk_per_trade,
            "max_daily_loss": self.config.max_daily_loss,
            "max_drawdown": self.config.max_drawdown,
        }
