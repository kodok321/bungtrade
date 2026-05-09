from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone, timedelta
from backend.database.session import get_db
from backend.database.models import User, Trade
from backend.api.deps import get_current_user
from backend.api.schemas import DashboardResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    all_trades_result = await db.execute(
        select(Trade).where(Trade.user_id == current_user.id)
    )
    all_trades = all_trades_result.scalars().all()

    open_trades = [t for t in all_trades if t.status == "open"]
    closed_trades = [t for t in all_trades if t.status in ("filled", "closed")]
    today_trades = [t for t in closed_trades if t.closed_at and t.closed_at >= today]

    total_pnl = sum(t.pnl for t in closed_trades)
    daily_profit = sum(t.pnl for t in today_trades)
    unrealized_pnl = sum(t.pnl for t in open_trades)

    winning = len([t for t in closed_trades if t.pnl > 0])
    total_closed = len(closed_trades)
    winrate = (winning / total_closed * 100) if total_closed > 0 else 0

    equity_curve = []
    running_balance = 10000.0
    for trade in sorted(closed_trades, key=lambda t: t.closed_at or t.opened_at):
        running_balance += trade.pnl
        equity_curve.append({
            "date": (trade.closed_at or trade.opened_at).isoformat(),
            "balance": round(running_balance, 2),
        })

    return DashboardResponse(
        total_balance=round(running_balance, 2),
        unrealized_pnl=round(unrealized_pnl, 2),
        daily_profit=round(daily_profit, 2),
        winrate=round(winrate, 1),
        active_positions=len(open_trades),
        total_trades=len(all_trades),
        equity_curve=equity_curve,
    )


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trade).where(Trade.user_id == current_user.id, Trade.status.in_(["filled", "closed"]))
    )
    trades = result.scalars().all()

    if not trades:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "winrate": 0,
            "total_pnl": 0,
            "avg_pnl": 0,
            "best_trade": 0,
            "worst_trade": 0,
            "avg_holding_time": 0,
        }

    pnls = [t.pnl for t in trades]
    winning = [p for p in pnls if p > 0]
    losing = [p for p in pnls if p < 0]

    return {
        "total_trades": len(trades),
        "winning_trades": len(winning),
        "losing_trades": len(losing),
        "winrate": round(len(winning) / len(trades) * 100, 1),
        "total_pnl": round(sum(pnls), 2),
        "avg_pnl": round(sum(pnls) / len(pnls), 2),
        "best_trade": round(max(pnls), 2),
        "worst_trade": round(min(pnls), 2),
    }
