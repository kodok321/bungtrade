from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.database.session import init_db
from backend.api.auth import router as auth_router
from backend.api.exchange_routes import router as exchange_router
from backend.api.trading_routes import router as trading_router
from backend.api.dashboard_routes import router as dashboard_router
from backend.api.settings_routes import router as settings_router
from backend.api.signal_routes import router as signal_router
from backend.api.backtest_routes import router as backtest_router
from backend.api.paper_routes import router as paper_router
from backend.api.market_routes import router as market_router
from backend.api.strategy_routes import router as strategy_router
from backend.api.risk_routes import router as risk_router
from backend.websocket_handlers.market_ws import binance_ws_proxy


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(exchange_router)
app.include_router(trading_router)
app.include_router(dashboard_router)
app.include_router(settings_router)
app.include_router(signal_router)
app.include_router(backtest_router)
app.include_router(paper_router)
app.include_router(market_router)
app.include_router(strategy_router)
app.include_router(risk_router)


@app.websocket("/ws/market/{symbol}")
async def market_websocket(websocket: WebSocket, symbol: str, stream: str = "ticker"):
    await binance_ws_proxy(websocket, symbol, stream)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
