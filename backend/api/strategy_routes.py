from fastapi import APIRouter, Depends
from backend.api.deps import get_current_user
from backend.database.models import User
from backend.strategies.registry import list_strategies

router = APIRouter(prefix="/api/strategies", tags=["Strategies"])


@router.get("/")
async def get_strategies(current_user: User = Depends(get_current_user)):
    return list_strategies()
