import asyncio
from typing import Optional
import ccxt.async_support as ccxt


class BinanceClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = False,
    ):
        config = {
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        }
        if api_key and api_secret:
            config["apiKey"] = api_key
            config["secret"] = api_secret
        if testnet:
            config["sandbox"] = True

        self.exchange = ccxt.binance(config)

    async def close(self):
        await self.exchange.close()

    async def get_account_balance(self) -> dict:
        try:
            balance = await self.exchange.fetch_balance()
            total = balance.get("total", {})
            free = balance.get("free", {})
            non_zero = {k: {"total": v, "free": free.get(k, 0)} for k, v in total.items() if v and v > 0}
            return {"balances": non_zero, "total_usdt": total.get("USDT", 0)}
        finally:
            await self.close()

    async def get_futures_balance(self) -> dict:
        try:
            self.exchange.options["defaultType"] = "future"
            balance = await self.exchange.fetch_balance()
            return {
                "total_balance": balance.get("total", {}).get("USDT", 0),
                "free_balance": balance.get("free", {}).get("USDT", 0),
            }
        finally:
            await self.close()

    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: Optional[float] = None,
        order_type: str = "MARKET",
    ) -> dict:
        try:
            if order_type == "LIMIT" and price:
                order = await self.exchange.create_limit_order(
                    symbol, side.lower(), quantity, price
                )
            else:
                order = await self.exchange.create_market_order(
                    symbol, side.lower(), quantity
                )
            return order
        finally:
            await self.close()

    async def get_ticker(self, symbol: str) -> dict:
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                "symbol": ticker["symbol"],
                "last": ticker["last"],
                "high": ticker["high"],
                "low": ticker["low"],
                "volume": ticker["baseVolume"],
                "change": ticker["percentage"],
                "bid": ticker["bid"],
                "ask": ticker["ask"],
            }
        finally:
            await self.close()

    async def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> list:
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, interval, limit=limit)
            return [
                {
                    "time": int(candle[0] / 1000),
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5],
                }
                for candle in ohlcv
            ]
        finally:
            await self.close()

    async def get_orderbook(self, symbol: str, limit: int = 20) -> dict:
        try:
            ob = await self.exchange.fetch_order_book(symbol, limit)
            return {
                "bids": [{"price": b[0], "qty": b[1]} for b in ob["bids"][:limit]],
                "asks": [{"price": a[0], "qty": a[1]} for a in ob["asks"][:limit]],
            }
        finally:
            await self.close()

    async def get_top_movers(self) -> list:
        try:
            tickers = await self.exchange.fetch_tickers()
            usdt_pairs = [
                {
                    "symbol": k,
                    "last": v["last"],
                    "change": v.get("percentage", 0),
                    "volume": v.get("quoteVolume", 0),
                }
                for k, v in tickers.items()
                if k.endswith("/USDT") and v.get("last")
            ]
            usdt_pairs.sort(key=lambda x: abs(x.get("change", 0) or 0), reverse=True)
            return usdt_pairs[:20]
        finally:
            await self.close()
