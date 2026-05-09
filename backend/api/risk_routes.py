from fastapi import APIRouter, Depends
from backend.api.deps import get_current_user
from backend.database.models import User
from backend.risk.manager import RiskManager

router = APIRouter(prefix="/api/risk", tags=["Risk Management"])

_risk_managers: dict[int, RiskManager] = {}


def get_risk_manager(user_id: int) -> RiskManager:
    if user_id not in _risk_managers:
        _risk_managers[user_id] = RiskManager()
    return _risk_managers[user_id]


@router.get("/status")
async def get_risk_status(current_user: User = Depends(get_current_user)):
    rm = get_risk_manager(current_user.id)
    return rm.get_status()


@router.post("/emergency-stop")
async def emergency_stop(current_user: User = Depends(get_current_user)):
    rm = get_risk_manager(current_user.id)
    rm.emergency_close_all()
    return {"message": "Emergency stop activated - all trading halted"}


@router.post("/resume")
async def resume_trading(current_user: User = Depends(get_current_user)):
    rm = get_risk_manager(current_user.id)
    rm.resume_trading()
    return {"message": "Trading resumed"}
