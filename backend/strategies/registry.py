from backend.strategies.base import BaseStrategy
from backend.strategies.ema_cross import EMACrossStrategy
from backend.strategies.rsi_strategy import RSIStrategy
from backend.strategies.macd_strategy import MACDStrategy
from backend.strategies.scalping import ScalpingStrategy
from backend.strategies.breakout import BreakoutStrategy

STRATEGY_REGISTRY: dict[str, type[BaseStrategy]] = {
    "ema_cross": EMACrossStrategy,
    "rsi": RSIStrategy,
    "macd": MACDStrategy,
    "scalping": ScalpingStrategy,
    "breakout": BreakoutStrategy,
}


def get_strategy(name: str, **kwargs) -> BaseStrategy:
    strategy_cls = STRATEGY_REGISTRY.get(name)
    if not strategy_cls:
        raise ValueError(f"Strategy '{name}' not found. Available: {list(STRATEGY_REGISTRY.keys())}")
    return strategy_cls(**kwargs)


def list_strategies() -> list[dict]:
    return [cls().get_info() for cls in STRATEGY_REGISTRY.values()]
