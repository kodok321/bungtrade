from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.database.session import get_db
from backend.database.models import User, BacktestResult
from backend.api.deps import get_current_user
from backend.api.schemas import BacktestRequest, BacktestResponse
from backend.backtesting.engine import BacktestEngine

router = APIRouter(prefix="/api/backtest", tags=["Backtesting"])


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(
    data: BacktestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    engine = BacktestEngine()
    try:
        result = await engine.run(
            strategy=data.strategy,
            symbol=data.symbol,
            timeframe=data.timeframe,
            start_date=data.start_date,
            end_date=data.end_date,
            initial_balance=data.initial_balance,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    backtest = BacktestResult(
        user_id=current_user.id,
        strategy=data.strategy,
        symbol=data.symbol,
        timeframe=data.timeframe,
        start_date=result["start_date"],
        end_date=result["end_date"],
        initial_balance=data.initial_balance,
        final_balance=result["final_balance"],
        total_trades=result["total_trades"],
        winning_trades=result["winning_trades"],
        losing_trades=result["losing_trades"],
        winrate=result["winrate"],
        max_drawdown=result["max_drawdown"],
        sharpe_ratio=result.get("sharpe_ratio"),
        profit_factor=result.get("profit_factor"),
        equity_curve=result.get("equity_curve"),
        monthly_returns=result.get("monthly_returns"),
        trades_log=result.get("trades_log"),
    )
    db.add(backtest)
    await db.flush()
    return BacktestResponse.model_validate(backtest)


@router.get("/results", response_model=list[BacktestResponse])
async def get_results(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BacktestResult)
        .where(BacktestResult.user_id == current_user.id)
        .order_by(desc(BacktestResult.created_at))
        .limit(limit)
    )
    return [BacktestResponse.model_validate(r) for r in result.scalars().all()]
