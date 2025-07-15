# utils/telegram.py

import requests
from typing import Dict, Any, Optional
from datetime import datetime

class CompleteTelegramNotifier:
    """Telegram bot using centralized parameters"""

    def __init__(self):
        from config import BotConfig
        
        self.bot_token = BotConfig.TELEGRAM_BOT_TOKEN.strip()
        self.chat_id = BotConfig.TELEGRAM_CHAT_ID.strip()
        self.base_url = f"https://api.telegram.org/bot {self.bot_token}"
        self.enabled = (
            BotConfig.TELEGRAM_ENABLED and 
            self.bot_token and 
            self.chat_id and 
            self.bot_token != "YOUR_TELEGRAM_BOT_TOKEN" and 
            self.chat_id != "YOUR_CHAT_ID"
        )

        if self.enabled:
            self._test_connection()
        else:
            print("⚠️ Telegram disabled – check credentials")

    def _test_connection(self):
        """Test Telegram bot connection"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=5)
            if response.status_code == 200:
                bot_info = response.json().get('result', {})
                print(f"✅ Telegram bot connected: {bot_info.get('first_name', 'Unknown')}")
                return True
            else:
                print(f"❌ Telegram bot connection failed: {response.status_code} - {response.text}")
                self.enabled = False
                return False
        except Exception as e:
            print(f"❌ Telegram connection error: {e}")
            self.enabled = False
            return False

    def _send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Actually send message to Telegram"""
        if not self.enabled:
            print(f"[Telegram] Disabled: {message[:30]}...")
            return False

        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }

            response = requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=10)

            if response.status_code == 200:
                print(f"[Telegram] Sent: {message[:50]}...")
                return True
            else:
                print(f"[Telegram] Send failed: {response.status_code} | {response.text}")
                return False
        except Exception as e:
            print(f"[Telegram] Network error: {e}")
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
