import logging
from typing import Optional
import aiohttp
from backend.core.config import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None

    async def send_message(self, text: str, chat_id: Optional[str] = None) -> bool:
        if not self.base_url:
            logger.warning("Telegram bot token not configured")
            return False
        target = chat_id or self.chat_id
        if not target:
            return False
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": target, "text": text, "parse_mode": "HTML"},
                ) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False

    async def send_signal_alert(self, signal: dict) -> bool:
        text = (
            f"<b>🔔 AI Signal Alert</b>\n\n"
            f"<b>{signal['side']}</b> {signal['symbol']}\n"
            f"Confidence: {signal['confidence']}%\n"
            f"Entry: {signal['entry_price']}\n"
            f"TP: {signal.get('take_profit', 'N/A')}\n"
            f"SL: {signal.get('stop_loss', 'N/A')}\n"
            f"Trend: {signal.get('trend', 'N/A')}\n"
            f"Strategy: {signal.get('strategy', 'N/A')}"
        )
        return await self.send_message(text)

    async def send_trade_alert(self, action: str, symbol: str, price: float, pnl: float = 0) -> bool:
        text = (
            f"<b>📊 Trade Alert</b>\n\n"
            f"Action: {action}\n"
            f"Symbol: {symbol}\n"
            f"Price: {price}\n"
            f"PNL: {pnl:+.2f} USDT"
        )
        return await self.send_message(text)

    async def send_daily_report(self, stats: dict) -> bool:
        text = (
            f"<b>📈 Daily Report</b>\n\n"
            f"Balance: {stats.get('balance', 0):.2f} USDT\n"
            f"Daily PNL: {stats.get('daily_pnl', 0):+.2f} USDT\n"
            f"Trades: {stats.get('total_trades', 0)}\n"
            f"Winrate: {stats.get('winrate', 0):.1f}%\n"
            f"Open Positions: {stats.get('open_positions', 0)}"
        )
        return await self.send_message(text)

    async def send_error_notification(self, error: str) -> bool:
        text = f"<b>⚠️ Error</b>\n\n{error}"
        return await self.send_message(text)
