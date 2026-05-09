from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database.session import get_db
from backend.database.models import User, ExchangeAPIKey
from backend.api.deps import get_current_user
from backend.api.schemas import ExchangeKeyCreate, ExchangeKeyResponse, TestConnectionResponse
from backend.core.security import encrypt_api_key, decrypt_api_key
from backend.exchange.binance_client import BinanceClient

router = APIRouter(prefix="/api/exchange", tags=["Exchange"])


@router.post("/keys", response_model=ExchangeKeyResponse)
async def add_api_key(
    data: ExchangeKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    key = ExchangeAPIKey(
        user_id=current_user.id,
        api_key_encrypted=encrypt_api_key(data.api_key),
        api_secret_encrypted=encrypt_api_key(data.api_secret),
        label=data.label,
        trading_mode=data.trading_mode,
        is_testnet=data.is_testnet,
    )
    db.add(key)
    await db.flush()
    return ExchangeKeyResponse(
        id=key.id,
        exchange=key.exchange,
        label=key.label,
        trading_mode=key.trading_mode,
        is_testnet=key.is_testnet,
        is_active=key.is_active,
        api_key_masked=data.api_key[:6] + "..." + data.api_key[-4:],
    )


@router.get("/keys", response_model=list[ExchangeKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExchangeAPIKey).where(ExchangeAPIKey.user_id == current_user.id)
    )
    keys = result.scalars().all()
    responses = []
    for key in keys:
        api_key = decrypt_api_key(key.api_key_encrypted)
        responses.append(
            ExchangeKeyResponse(
                id=key.id,
                exchange=key.exchange,
                label=key.label,
                trading_mode=key.trading_mode,
                is_testnet=key.is_testnet,
                is_active=key.is_active,
                api_key_masked=api_key[:6] + "..." + api_key[-4:],
            )
        )
    return responses


@router.delete("/keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExchangeAPIKey).where(
            ExchangeAPIKey.id == key_id, ExchangeAPIKey.user_id == current_user.id
        )
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    await db.delete(key)
    return {"message": "API key deleted"}


@router.post("/test-connection/{key_id}", response_model=TestConnectionResponse)
async def test_connection(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExchangeAPIKey).where(
            ExchangeAPIKey.id == key_id, ExchangeAPIKey.user_id == current_user.id
        )
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    try:
        api_key = decrypt_api_key(key.api_key_encrypted)
        api_secret = decrypt_api_key(key.api_secret_encrypted)
        client = BinanceClient(
            api_key=api_key,
            api_secret=api_secret,
            testnet=key.is_testnet,
        )
        balance = await client.get_account_balance()
        return TestConnectionResponse(
            success=True, message="Connection successful", balance=balance
        )
    except Exception as e:
        return TestConnectionResponse(success=False, message=str(e))


@router.get("/balance/{key_id}")
async def get_balance(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExchangeAPIKey).where(
            ExchangeAPIKey.id == key_id, ExchangeAPIKey.user_id == current_user.id
        )
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key = decrypt_api_key(key.api_key_encrypted)
    api_secret = decrypt_api_key(key.api_secret_encrypted)
    client = BinanceClient(
        api_key=api_key, api_secret=api_secret, testnet=key.is_testnet
    )

    if key.trading_mode == "futures":
        balance = await client.get_futures_balance()
    else:
        balance = await client.get_account_balance()

    return balance
