import asyncio
import logging
from typing import Optional
from backend.exchange.binance_client import BinanceClient
from backend.ai.signal_engine import AISignalEngine
from backend.risk.manager import RiskManager, RiskConfig
from backend.strategies.registry import get_strategy

logger = logging.getLogger(__name__)


class AutoTrader:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        testnet: bool = False,
        risk_config: Optional[RiskConfig] = None,
        mode: str = "manual",
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.risk_manager = RiskManager(risk_config)
        self.signal_engine = AISignalEngine()
        self.mode = mode
        self.is_running = False
        self.active_strategy = "ema_cross"
        self._monitored_pairs = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

    async def start(self):
        if self.mode == "manual":
            logger.info("Auto trader in manual mode - not starting")
            return
        self.is_running = True
        logger.info(f"Auto trader started in {self.mode} mode")
        while self.is_running:
            try:
                await self._trading_loop()
            except Exception as e:
                logger.error(f"Auto trader error: {e}")
            await asyncio.sleep(60)

    async def stop(self):
        self.is_running = False
        logger.info("Auto trader stopped")

    async def _trading_loop(self):
        for symbol in self._monitored_pairs:
            can_trade, reason = self.risk_manager.can_open_trade()
            if not can_trade:
                logger.info(f"Cannot trade: {reason}")
                return

            signal = await self.signal_engine.generate_signal(symbol, "1h")
            if signal["confidence"] < 60:
                continue

            if self.mode == "semi_auto":
                logger.info(f"Semi-auto signal: {signal['side']} {symbol} @ {signal['confidence']}% confidence")
                continue

            if self.mode == "full_auto":
                await self._execute_trade(signal)

    async def _execute_trade(self, signal: dict):
        try:
            client = BinanceClient(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=self.testnet,
            )
            position_size = self.risk_manager.calculate_position_size(
                signal["entry_price"], signal["stop_loss"]
            )
            if position_size <= 0:
                return

            order = await client.place_order(
                symbol=signal["symbol"],
                side=signal["side"],
                quantity=position_size,
            )
            self.risk_manager.open_positions += 1
            logger.info(f"Executed: {signal['side']} {signal['symbol']} qty={position_size}")
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
