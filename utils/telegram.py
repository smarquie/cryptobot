# utils/telegram.py

import requests
from typing import Dict, Any, Optional
from datetime import datetime
from config import BotConfig  # ← Add this line
import logging

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Telegram bot using centralized parameters from config"""

    def __init__(self):
        from config import BotConfig
        
        # Load token/chat_id directly from config
        self.bot_token = BotConfig.TELEGRAM_BOT_TOKEN.strip()
        self.chat_id = BotConfig.TELEGRAM_CHAT_ID.strip()
        
        # Validate credentials
        self.enabled = (
            self.bot_token and self.chat_id and 
            self.bot_token != "your_telegram_token_here" and 
            self.chat_id != "your_chat_id" and
            not self.bot_token.startswith("YOUR_") and
            not self.chat_id.startswith("YOUR_")
        )

        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        if self.enabled:
            success = self._test_connection()
            if success:
                self._send_startup_message()
            else:
                self.enabled = False
        else:
            print("⚠️ Telegram disabled – check credentials")

    def _test_connection(self):
        """Test Telegram bot connection"""
        test_url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
        try:
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                bot_info = response.json().get('result', {})
                logger.info(f"✅ Telegram bot connected: {bot_info.get('first_name', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ Telegram bot failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Telegram connection error: {e}")
            return False

    def _send_startup_message(self):
        """Send startup message to Telegram"""
        message = (
            f"🚀 *Trading Bot Started*\n"
            f"📅 Time: {datetime.now().strftime('%H:%M:%S')}\n"
            f"⚙️ Mode: {BotConfig.MODE.upper()}\n"
            f"📊 Symbols: {', '.join(BotConfig.TRADING_SYMBOLS)}"
        )
        success = self._send_message(message)
        if success:
            logger.info("✅ Telegram startup message sent")
        return success
    
    def _send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Actually send message to Telegram"""
        if not self.enabled:
            logger.warning(f"[Telegram] Disabled: {message[:30]}...")
            return False

        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }

            response = requests.post(self.base_url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"[Telegram] Sent: {message[:50]}...")
                return True
            else:
                logger.error(f"[Telegram] Send failed: {response.status_code} | {response.text}")
                return False
        except Exception as e:
            logger.error(f"[Telegram] Network error: {e}")
            return False

    def send_position_opened(self, symbol: str, side: str, size: float, entry_price: float, strategy: str, reason: str, target_hold: str, portfolio_summary: Dict) -> bool:
        emoji = "🟢" if side == "buy" else "🔴"
        position_value = size * entry_price

        strategy_emoji = {
            "Ultra-Scalp": "⚡",
            "Fast-Scalp": "🔥",
            "Quick-Momentum": "📈",
            "TTM-Squeeze": "🎯"
        }.get(strategy, "📊")

        message = f"""
{emoji} <b>POSITION OPENED</b>

📊 <b>Symbol:</b> {symbol}
📈 <b>Side:</b> {side.upper()}
💰 <b>Size:</b> {size:.4f}
💵 <b>Entry:</b> ${entry_price:,.2f}
💎 <b>Position Value:</b> ${position_value:,.2f}
{strategy_emoji} <b>Strategy:</b> {strategy}
⚡ <b>Target Hold:</b> {target_hold}

📊 <b>PORTFOLIO STATUS:</b>
💰 <b>Total Value:</b> ${portfolio_summary['total_value']:,.2f}
📈 <b>Total Return:</b> {portfolio_summary['total_return_pct']:+.2f}%
📋 <b>Open Positions:</b> {portfolio_summary['open_positions']}
🎯 <b>Win Rate:</b> {portfolio_summary['win_rate']:.1f}%

⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
        """
        return self._send_message(message.strip())

    def send_position_closed(self, symbol: str, side: str, size: float, entry_price: float, close_price: float, pnl: float, reason: str, strategy: str, hold_duration: str, portfolio_summary: Dict) -> bool:
        profit_emoji = "💚" if pnl > 0 else "❤️" if pnl < 0 else "💛"
        pnl_pct = (pnl / (size * entry_price)) * 100
        position_value = size * entry_price

        strategy_emoji = {
            "Ultra-Scalp": "⚡",
            "Fast-Scalp": "🔥",
            "Quick-Momentum": "📈",
            "TTM-Squeeze": "🎯"
        }.get(strategy, "📊")

        message = f"""
{profit_emoji} <b>POSITION CLOSED</b>

📊 <b>Symbol:</b> {symbol}
📈 <b>Side:</b> {side.upper()}
💰 <b>Size:</b> {size:.4f}
💵 <b>Entry:</b> ${entry_price:,.2f}
💵 <b>Exit:</b> ${close_price:,.2f}
💎 <b>Position Value:</b> ${position_value:,.2f}

💸 <b>P&L:</b> ${pnl:,.2f} ({pnl_pct:+.2f}%)
⏱ <b>Hold Time:</b> {hold_duration}
{strategy_emoji} <b>Strategy:</b> {strategy}
📝 <b>Exit:</b> {reason}

📊 <b>PORTFOLIO STATUS:</b>
💰 <b>Total Value:</b> ${portfolio_summary['total_value']:,.2f}
📈 <b>Total Return:</b> {portfolio_summary['total_return_pct']:+.2f}%
📋 <b>Open Positions:</b> {portfolio_summary['open_positions']}
🎯 <b>Win Rate:</b> {portfolio_summary['win_rate']:.1f}%

⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
        """
        return self._send_message(message.strip())
