# utils/telegram.py

import requests
from typing import Optional

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        # Enable only if both token and chat ID are provided and not default
        self.enabled = (
            bot_token and chat_id and 
            bot_token != "your_telegram_token_here" and 
            chat_id != "your_chat_id_here"
        )
        
        self.base_url = f"https://api.telegram.org/bot {self.bot_token}/sendMessage"

    def send_message(self, text: str) -> bool:
        """Send raw message to Telegram"""
        if not self.enabled:
            print(f"[Telegram] Disabled: {text[:50]}...")
            return False

        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'MarkdownV2'
        }

        try:
            response = requests.post(self.base_url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"[Telegram] Sent: {text[:50]}...")
                return True
            else:
                print(f"[Telegram] Send failed: {response.text}")
                return False
        except Exception as e:
            print(f"[Telegram] Error sending message: {e}")
            return False

    def send_position_opened(self, symbol: str, action: str, price: float, confidence: float, reason: str = "") -> None:
        message = (
            f"*🟢 Position Opened*\n\n"
            f"Symbol: `{symbol}`\n"
            f"Action: *{action.upper()}*\n"
            f"Price: ${price:.2f}\n"
            f"Confidence: _{confidence:.2f}_\n"
            f"Reason: `{reason}`"
        )
        self.send_message(message)

    def send_position_closed(self, symbol: str, action: str, exit_price: float, pnl: float) -> None:
        emoji = "📈" if action == "buy" else "📉"
        message = (
            f"{emoji} *Position Closed*\n\n"
            f"Symbol: `{symbol}`\n"
            f"Exit Price: ${exit_price:.2f}\n"
            f"P&L: ${pnl:.2f}"
        )
        self.send_message(message)

    def send_status_update(self, summary: dict) -> None:
        message = (
            f"📊 *Bot Status Update*\n\n"
            f"Balance: ${summary['balance']:,.2f}\n"
            f"Total Value: ${summary['total_value']:,.2f}\n"
            f"Positions: {summary['open_positions']}\n"
            f"P&L: ${summary['unrealized_pnl']:,.2f}\n"
            f"Exposure: {summary['exposure_pct']:.1f}%"
        )
        self.send_message(message)

    def send_error_alert(self, error: str) -> None:
        message = (
            f"❌ *Critical Error*\n\n"
            f"`{error}`"
        )
        self.send_message(message)
            f"P&L: ${pnl:.2f}"
        )
        self.send_message(message)
