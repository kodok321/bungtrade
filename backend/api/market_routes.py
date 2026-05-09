from fastapi import APIRouter, Query
from backend.exchange.binance_client import BinanceClient

router = APIRouter(prefix="/api/market", tags=["Market Data"])


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    client = BinanceClient()
    return await client.get_ticker(symbol)


@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    interval: str = Query(default="1h"),
    limit: int = Query(default=100),
):
    client = BinanceClient()
    return await client.get_klines(symbol, interval, limit)


@router.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = Query(default=20)):
    client = BinanceClient()
    return await client.get_orderbook(symbol, limit)


@router.get("/top-movers")
async def get_top_movers():
    client = BinanceClient()
    return await client.get_top_movers()


@router.get("/fear-greed")
async def get_fear_greed():
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.alternative.me/fng/?limit=1") as resp:
                data = await resp.json()
                return data.get("data", [{}])[0]
    except Exception:
        return {"value": "50", "value_classification": "Neutral"}
