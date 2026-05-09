from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.database.session import get_db
from backend.database.models import User, Signal
from backend.api.deps import get_current_user
from backend.api.schemas import SignalResponse
from backend.ai.signal_engine import AISignalEngine

router = APIRouter(prefix="/api/signals", tags=["Signals"])


@router.get("/", response_model=list[SignalResponse])
async def get_signals(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Signal).where(Signal.is_active == True).order_by(desc(Signal.created_at)).limit(limit)
    )
    return [SignalResponse.model_validate(s) for s in result.scalars().all()]


@router.post("/generate")
async def generate_signal(
    symbol: str = Query(default="BTCUSDT"),
    timeframe: str = Query(default="1h"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    engine = AISignalEngine()
    signal_data = await engine.generate_signal(symbol, timeframe)

    signal = Signal(
        symbol=signal_data["symbol"],
        side=signal_data["side"],
        confidence=signal_data["confidence"],
        entry_price=signal_data["entry_price"],
        take_profit=signal_data.get("take_profit"),
        stop_loss=signal_data.get("stop_loss"),
        trend=signal_data.get("trend"),
        timeframe=timeframe,
        strategy=signal_data.get("strategy"),
        analysis=signal_data.get("analysis"),
    )
    db.add(signal)
    await db.flush()

    return SignalResponse.model_validate(signal)


@router.get("/scanner")
async def scan_pairs(
    current_user: User = Depends(get_current_user),
):
    engine = AISignalEngine()
    pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT",
             "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT"]
    results = []
    for pair in pairs:
        try:
            signal = await engine.generate_signal(pair, "1h")
            results.append(signal)
        except Exception:
            continue
    results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    return results
