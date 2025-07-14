# utils/telegram.py

import requests
from typing import Optional

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.enabled = token and chat_id and token != "YOUR_TELEGRAM_BOT_TOKEN" and chat_id != "YOUR_CHAT_ID"

    def send_message(self, message: str):
        if not self.enabled:
            print(f"[Telegram] Disabled: {message[:50]}...")
            return False

        url = f"https://api.telegram.org/bot {self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "MarkdownV2"
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"[Telegram] Error sending message: {e}")
            return False

    def send_position_opened(self, symbol: str, action: str, price: float, confidence: float, reason: str):
        message = (
            f"*🟢 Position Opened*\n\n"
            f"Symbol: `{symbol}`\n"
            f"Action: *{action.upper()}*\n"
            f"Price: ${price:.2f}\n"
            f"Confidence: _{confidence:.2f}_\n"
            f"Reason: `{reason}`"
        )
        self.send_message(message)

    def send_position_closed(self, symbol: str, action: str, exit_price: float, pnl: float):
        emoji = "📈" if action == "buy" else "📉"
        message = (
            f"{emoji} *Position Closed*\n\n"
            f"Symbol: `{symbol}`\n"
            f"Exit Price: ${exit_price:.2f}\n"
            f"P&L: ${pnl:.2f}"
        )
        self.send_message(message)