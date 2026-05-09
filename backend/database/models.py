from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from backend.database.session import Base


class TradingMode(str, enum.Enum):
    SPOT = "spot"
    FUTURES = "futures"


class OrderSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


class AutoTradingMode(str, enum.Enum):
    MANUAL = "manual"
    SEMI_AUTO = "semi_auto"
    FULL_AUTO = "full_auto"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    api_keys = relationship("ExchangeAPIKey", back_populates="user", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    paper_accounts = relationship("PaperAccount", back_populates="user", cascade="all, delete-orphan")


class ExchangeAPIKey(Base):
    __tablename__ = "exchange_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange = Column(String(50), default="binance")
    label = Column(String(100), default="Default")
    api_key_encrypted = Column(Text, nullable=False)
    api_secret_encrypted = Column(Text, nullable=False)
    trading_mode = Column(String(20), default=TradingMode.SPOT.value)
    is_testnet = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    ip_whitelist = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="api_keys")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    trailing_stop = Column(Float, nullable=True)
    status = Column(String(20), default=OrderStatus.OPEN.value)
    pnl = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    fee = Column(Float, default=0.0)
    strategy = Column(String(50), nullable=True)
    trading_mode = Column(String(20), default=TradingMode.SPOT.value)
    is_paper = Column(Boolean, default=False)
    order_id = Column(String(100), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    opened_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="trades")


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    confidence = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    trend = Column(String(20), nullable=True)
    timeframe = Column(String(10), nullable=True)
    strategy = Column(String(50), nullable=True)
    analysis = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    auto_trading_mode = Column(String(20), default=AutoTradingMode.MANUAL.value)
    risk_per_trade = Column(Float, default=2.0)
    max_daily_loss = Column(Float, default=5.0)
    max_drawdown = Column(Float, default=10.0)
    max_concurrent_trades = Column(Integer, default=5)
    default_leverage = Column(Integer, default=1)
    preferred_pairs = Column(JSON, default=list)
    telegram_enabled = Column(Boolean, default=False)
    telegram_chat_id = Column(String(100), nullable=True)
    paper_trading = Column(Boolean, default=False)
    active_strategy = Column(String(50), default="ema_cross")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="settings")


class PaperAccount(Base):
    __tablename__ = "paper_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Float, default=10000.0)
    initial_balance = Column(Float, default=10000.0)
    total_pnl = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="paper_accounts")


class AILog(Base):
    __tablename__ = "ai_logs"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False)
    action = Column(String(20), nullable=False)
    confidence = Column(Float)
    reasoning = Column(Text)
    indicators = Column(JSON)
    result = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    strategy = Column(String(50), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    initial_balance = Column(Float, default=10000.0)
    final_balance = Column(Float)
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    winrate = Column(Float)
    max_drawdown = Column(Float)
    sharpe_ratio = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    equity_curve = Column(JSON, nullable=True)
    monthly_returns = Column(JSON, nullable=True)
    trades_log = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
