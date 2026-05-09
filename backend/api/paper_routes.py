from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database.session import get_db
from backend.database.models import User, PaperAccount
from backend.api.deps import get_current_user
from backend.api.schemas import PaperAccountCreate, PaperAccountResponse

router = APIRouter(prefix="/api/paper", tags=["Paper Trading"])


@router.post("/account", response_model=PaperAccountResponse)
async def create_paper_account(
    data: PaperAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    account = PaperAccount(
        user_id=current_user.id,
        balance=data.initial_balance,
        initial_balance=data.initial_balance,
    )
    db.add(account)
    await db.flush()
    return PaperAccountResponse.model_validate(account)


@router.get("/account", response_model=list[PaperAccountResponse])
async def get_paper_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PaperAccount).where(PaperAccount.user_id == current_user.id)
    )
    return [PaperAccountResponse.model_validate(a) for a in result.scalars().all()]


@router.post("/reset/{account_id}", response_model=PaperAccountResponse)
async def reset_paper_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PaperAccount).where(
            PaperAccount.id == account_id, PaperAccount.user_id == current_user.id
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Paper account not found")

    account.balance = account.initial_balance
    account.total_pnl = 0.0
    account.total_trades = 0
    account.winning_trades = 0
    account.losing_trades = 0
    await db.flush()
    return PaperAccountResponse.model_validate(account)
