# trading_engine.py

import asyncio
import logging
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional

# Local imports
from config import BotConfig
from utils.exchange import CoinbaseExchange
from utils.telegram import TelegramNotifier
from strategies.ultra_scalp import UltraScalpStrategy
from strategies.fast_scalp import FastScalpStrategy
from strategies.quick_momentum import QuickMomentumStrategy
from strategies.ttm_squeeze import TTMSqueezeStrategy
from utils.logger import setup_logger

# Global state
GLOBAL_BOT_STATE = {
    'running': False,
    'engine': None,
    'task': None,
    'stop_requested': False
}

setup_logger()
logger = logging.getLogger(__name__)

@dataclass
class Position:
    symbol: str
    side: str
    size: float
    entry_price: float
    strategy: str
    stop_loss: float
    take_profit: float
    entry_time: datetime

class Portfolio:
    def __init__(self, initial_balance: float = 100000.0):
        self.balance = initial_balance
        self.positions: Dict[str, Position] = {}

    def open_position(self, signal: Dict, symbol: str, price: float):
        if symbol in self.positions:
            return False

        self.positions[symbol] = Position(**{
            'symbol': symbol,
            'side': signal['action'],
            'size': signal['position_size'],
            'entry_price': price,
            'strategy': signal['strategy'],
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'entry_time': datetime.now()
        })
        self.balance -= signal['position_size'] * price
        return True

    def close_position(self, symbol: str, price: float):
        if symbol not in self.positions:
            return False

        pos = self.positions.pop(symbol)
        pnl = (price - pos.entry_price) * pos.size if pos.side == 'buy' else (pos.entry_price - price) * pos.size
        self.balance += price * pos.size
        return pnl

    def get_portfolio_summary(self):
        return {
            'balance': self.balance,
            'positions': list(self.positions.keys()),
            'total_value': self.balance + sum(p.size * p.entry_price for p in self.positions.values())
        }

class SignalAggregator:
    def __init__(self):
        self.strategies = [
            UltraScalpStrategy(),
            FastScalpStrategy(),
            QuickMomentumStrategy(),
            TTMSqueezeStrategy()
        ]
        self.weights = {
            "Ultra-Scalp": 0.8,
            "Fast-Scalp": 0.9,
            "Quick-Momentum": 1.0,
            "TTM-Squeeze": 1.1
        }

    def aggregate(self, df: pd.DataFrame, symbol: str) -> Dict:
        signals = [s.analyze_and_signal(df, symbol) for s in self.strategies]
        valid_signals = [s for s in signals if s['confidence'] >= BotConfig.ULTRA_SCALP_MIN_CONFIDENCE]

        if not valid_signals:
            return {'action': 'hold', 'confidence': 0.0, 'reason': 'No valid signals'}

        best_signal = max(valid_signals, key=lambda x: x['confidence'] * self.weights[x['strategy']])
        return best_signal

class TradingEngine:
    def __init__(self):
        self.config = BotConfig
        self.portfolio = Portfolio()
        self.data_client = CoinbaseExchange(
            BotConfig.COINBASE_API_KEY,
            BotConfig.COINBASE_API_SECRET,
            BotConfig.COINBASE_PASSPHRASE
        )
        self.aggregator = SignalAggregator()
        self.telegram = TelegramNotifier(BotConfig.TELEGRAM_BOT_TOKEN, BotConfig.TELEGRAM_CHAT_ID)
        self.is_running = False
        self.data_client.product_ids = BotConfig.TRADING_SYMBOLS

    async def start_trading(self):
        self.is_running = True
        logger.info("🚀 Trading engine started")
        while self.is_running:
            await self.trading_cycle()
            await asyncio.sleep(BotConfig.CYCLE_INTERVAL)

    async def trading_cycle(self):
        try:
            market_data = self.data_client.get_market_data()
            for symbol in BotConfig.TRADING_SYMBOLS:
                df = self.data_client.get_candles_df(symbol, BotConfig.TIMEFRAME, BotConfig.MIN_DATA_MINUTES)
                signal = self.aggregator.aggregate(df, symbol)
                if signal['action'] != 'hold':
                    logger.info(f"📈 Signal: {signal['strategy']} → {signal['action'].upper()} on {symbol}")
                    if self.telegram.enabled:
                        self.telegram.send_message(
                            f"*Signal*\n"
                            f"Strategy: {signal['strategy']}\n"
                            f"Action: {signal['action'].upper()}\n"
                            f"Symbol: {symbol}\n"
                            f"Confidence: {signal['confidence']:.2f}\n"
                            f"Reason: {signal['reason']}"
                        )
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")

    async def stop(self):
        self.is_running = False
        logger.info("🛑 Trading engine stopped")

# ==================== GLOBAL CONTROL ====================
async def start_bot():
    global GLOBAL_BOT_STATE
    if GLOBAL_BOT_STATE['running']:
        print("⚠️ Bot already running")
        return

    engine = TradingEngine()
    GLOBAL_BOT_STATE.update({
        'engine': engine,
        'running': True,
        'task': asyncio.create_task(engine.start_trading())
    })
    print("✅ Bot started in background")

def complete_stop_bot():
    global GLOBAL_BOT_STATE
    if not GLOBAL_BOT_STATE['running']:
        print("⚠️ Bot not running")
        return

    engine = GLOBAL_BOT_STATE['engine']
    asyncio.run(engine.stop())
    GLOBAL_BOT_STATE.update({'running': False, 'engine': None, 'task': None})
    print("🛑 Bot stopped")

def check_status():
    engine = GLOBAL_BOT_STATE['engine']
    if engine:
        summary = engine.portfolio.get_portfolio_summary()
        print(f"💼 Balance: ${summary['balance']:,.2f}")
        print(f"📊 Open Positions: {len(summary['positions'])}")
        print(f"📈 Total Value: ${summary['total_value']:,.2f}")
    else:
        print("❌ Bot not running")