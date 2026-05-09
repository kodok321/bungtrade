from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Auth
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True


# Exchange
class ExchangeKeyCreate(BaseModel):
    api_key: str
    api_secret: str
    label: str = "Default"
    trading_mode: str = "spot"
    is_testnet: bool = False


class ExchangeKeyResponse(BaseModel):
    id: int
    exchange: str
    label: str
    trading_mode: str
    is_testnet: bool
    is_active: bool
    api_key_masked: str

    class Config:
        from_attributes = True


class TestConnectionResponse(BaseModel):
    success: bool
    message: str
    balance: Optional[dict] = None


# Trading
class OrderCreate(BaseModel):
    symbol: str
    side: str
    quantity: float
    price: Optional[float] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    trailing_stop: Optional[float] = None
    strategy: Optional[str] = None
    is_paper: bool = False


class TradeResponse(BaseModel):
    id: int
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    take_profit: Optional[float]
    stop_loss: Optional[float]
    status: str
    pnl: float
    pnl_percent: float
    strategy: Optional[str]
    is_paper: bool
    opened_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Settings
class UserSettingsUpdate(BaseModel):
    auto_trading_mode: Optional[str] = None
    risk_per_trade: Optional[float] = None
    max_daily_loss: Optional[float] = None
    max_drawdown: Optional[float] = None
    max_concurrent_trades: Optional[int] = None
    default_leverage: Optional[int] = None
    preferred_pairs: Optional[list[str]] = None
    telegram_enabled: Optional[bool] = None
    telegram_chat_id: Optional[str] = None
    paper_trading: Optional[bool] = None
    active_strategy: Optional[str] = None


class UserSettingsResponse(BaseModel):
    auto_trading_mode: str
    risk_per_trade: float
    max_daily_loss: float
    max_drawdown: float
    max_concurrent_trades: int
    default_leverage: int
    preferred_pairs: list
    telegram_enabled: bool
    paper_trading: bool
    active_strategy: str

    class Config:
        from_attributes = True


# Signal
class SignalResponse(BaseModel):
    id: int
    symbol: str
    side: str
    confidence: float
    entry_price: float
    take_profit: Optional[float]
    stop_loss: Optional[float]
    trend: Optional[str]
    timeframe: Optional[str]
    strategy: Optional[str]
    analysis: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


# Backtest
class BacktestRequest(BaseModel):
    strategy: str
    symbol: str
    timeframe: str = "1h"
    start_date: str
    end_date: str
    initial_balance: float = 10000.0


class BacktestResponse(BaseModel):
    id: int
    strategy: str
    symbol: str
    timeframe: str
    initial_balance: float
    final_balance: Optional[float]
    total_trades: Optional[int]
    winning_trades: Optional[int]
    losing_trades: Optional[int]
    winrate: Optional[float]
    max_drawdown: Optional[float]
    sharpe_ratio: Optional[float]
    profit_factor: Optional[float]
    equity_curve: Optional[list]
    monthly_returns: Optional[dict]

    class Config:
        from_attributes = True


# Dashboard
class DashboardResponse(BaseModel):
    total_balance: float
    unrealized_pnl: float
    daily_profit: float
    winrate: float
    active_positions: int
    total_trades: int
    equity_curve: list
    ai_recommendation: Optional[dict] = None


# Paper Trading
class PaperAccountCreate(BaseModel):
    initial_balance: float = 10000.0


class PaperAccountResponse(BaseModel):
    id: int
    balance: float
    initial_balance: float
    total_pnl: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    is_active: bool

    class Config:
        from_attributes = True


TokenResponse.model_rebuild()
