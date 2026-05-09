from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timezone
from backend.database.session import get_db
from backend.database.models import User, Trade, ExchangeAPIKey
from backend.api.deps import get_current_user
from backend.api.schemas import OrderCreate, TradeResponse
from backend.core.security import decrypt_api_key
from backend.exchange.binance_client import BinanceClient

router = APIRouter(prefix="/api/trading", tags=["Trading"])


async def _fetch_market_price(symbol: str) -> float:
    client = BinanceClient()
    try:
        ticker = await client.get_ticker(symbol)
        return float(ticker["last"])
    except Exception:
        return 0.0


def _calc_pnl(side: str, entry_price: float, exit_price: float, quantity: float):
    if side.lower() == "buy":
        pnl = (exit_price - entry_price) * quantity
    else:
        pnl = (entry_price - exit_price) * quantity
    cost = entry_price * quantity
    pnl_percent = (pnl / cost * 100) if cost > 0 else 0.0
    return round(pnl, 4), round(pnl_percent, 2)


@router.post("/order", response_model=TradeResponse)
async def place_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if order.is_paper:
        entry_price = order.price
        if not entry_price:
            entry_price = await _fetch_market_price(order.symbol)
        trade = Trade(
            user_id=current_user.id,
            symbol=order.symbol,
            side=order.side,
            entry_price=entry_price,
            quantity=order.quantity,
            take_profit=order.take_profit,
            stop_loss=order.stop_loss,
            trailing_stop=order.trailing_stop,
            strategy=order.strategy,
            is_paper=True,
            status="open",
        )
        db.add(trade)
        await db.flush()
        return TradeResponse.model_validate(trade)

    result = await db.execute(
        select(ExchangeAPIKey).where(
            ExchangeAPIKey.user_id == current_user.id,
            ExchangeAPIKey.is_active == True,
        ).limit(1)
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=400, detail="No active API key found")

    api_key = decrypt_api_key(key.api_key_encrypted)
    api_secret = decrypt_api_key(key.api_secret_encrypted)
    client = BinanceClient(api_key=api_key, api_secret=api_secret, testnet=key.is_testnet)

    try:
        exchange_order = await client.place_order(
            symbol=order.symbol,
            side=order.side.upper(),
            quantity=order.quantity,
            price=order.price,
            order_type="LIMIT" if order.price else "MARKET",
        )
        trade = Trade(
            user_id=current_user.id,
            symbol=order.symbol,
            side=order.side,
            entry_price=float(exchange_order.get("price", order.price or 0)),
            quantity=order.quantity,
            take_profit=order.take_profit,
            stop_loss=order.stop_loss,
            trailing_stop=order.trailing_stop,
            strategy=order.strategy,
            order_id=str(exchange_order.get("orderId", "")),
            status="open",
            trading_mode=key.trading_mode,
        )
        db.add(trade)
        await db.flush()
        return TradeResponse.model_validate(trade)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/positions", response_model=list[TradeResponse])
async def get_positions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trade)
        .where(Trade.user_id == current_user.id, Trade.status == "open")
        .order_by(desc(Trade.opened_at))
    )
    return [TradeResponse.model_validate(t) for t in result.scalars().all()]


@router.get("/history", response_model=list[TradeResponse])
async def get_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trade)
        .where(Trade.user_id == current_user.id)
        .order_by(desc(Trade.opened_at))
        .limit(limit)
    )
    return [TradeResponse.model_validate(t) for t in result.scalars().all()]


@router.post("/close/{trade_id}", response_model=TradeResponse)
async def close_trade(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trade).where(Trade.id == trade_id, Trade.user_id == current_user.id)
    )
    trade = result.scalar_one_or_none()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    if trade.status != "open":
        raise HTTPException(status_code=400, detail="Trade is not open")

    exit_price = await _fetch_market_price(trade.symbol)
    pnl, pnl_percent = _calc_pnl(trade.side, trade.entry_price, exit_price, trade.quantity)

    trade.exit_price = exit_price
    trade.pnl = pnl
    trade.pnl_percent = pnl_percent
    trade.status = "filled"
    trade.closed_at = datetime.now(timezone.utc)
    await db.flush()
    return TradeResponse.model_validate(trade)


@router.post("/close-all")
async def close_all_positions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trade).where(Trade.user_id == current_user.id, Trade.status == "open")
    )
    trades = result.scalars().all()
    closed_count = 0
    now = datetime.now(timezone.utc)
    for trade in trades:
        exit_price = await _fetch_market_price(trade.symbol)
        pnl, pnl_percent = _calc_pnl(trade.side, trade.entry_price, exit_price, trade.quantity)
        trade.exit_price = exit_price
        trade.pnl = pnl
        trade.pnl_percent = pnl_percent
        trade.status = "filled"
        trade.closed_at = now
        closed_count += 1
    await db.flush()
    return {"message": f"Closed {closed_count} positions"}
