# trading_engine.py

import pandas as pd
import numpy as np
from typing import Dict, Any
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List

# Local imports
from utils.wallet import validate_private_key
from config import BotConfig
from strategies import UltraScalpStrategy, FastScalpStrategy, QuickMomentumStrategy, TTMSqueezeStrategy
from strategies.signal_aggregator import SignalAggregator
from utils.exchange import ExchangeInterface
from utils.telegram import TelegramNotifier
from utils.logger import setup_logger
from utils.portfolio import Portfolio

setup_logger()
logger = logging.getLogger(__name__)

# Global state
GLOBAL_BOT_STATE = {
    'running': False,
    'engine': None,
    'task': None,
    'stop_requested': False
}

class SignalAggregator:
    def __init__(self):
        self.strategies = [
            UltraScalpStrategy(),
            FastScalpStrategy(),
            QuickMomentumStrategy(),
            TTMSqueezeStrategy()
        ]
        self.weights = BotConfig.STRATEGY_WEIGHTS

    def aggregate(self, df: pd.DataFrame, symbol: str) -> Dict:
        signals = [s.analyze_and_signal(df, symbol) for s in self.strategies]
        valid_signals = [s for s in signals if s['confidence'] >= BotConfig.ULTRA_SCALP_MIN_CONFIDENCE]
        if not valid_signals:
            return {'action': 'hold', 'confidence': 0.0, 'reason': 'No valid signals'}
        best = max(valid_signals, key=lambda x: x['confidence'] * self.weights[x['strategy']])
        return best

class TradingEngine:
    def __init__(self):
        self.config = BotConfig
        self.private_key = BotConfig.HYPERLIQUID_PRIVATE_KEY
        self.wallet = validate_private_key(self.private_key)
        self.exchange = ExchangeInterface(mode=BotConfig.MODE, private_key=self.private_key)
        self.portfolio = Portfolio()
        self.aggregator = SignalAggregator()
        self.telegram = TelegramNotifier(
            BotConfig.TELEGRAM_BOT_TOKEN,
            BotConfig.TELEGRAM_CHAT_ID
        )        
        self.is_running = False
        self.cycle_count = 0
        self.symbols = BotConfig.TRADING_SYMBOLS

    async def start_trading(self):
        self.is_running = True
        logger.info("🚀 Trading engine started")
        while self.is_running:
            await self.trading_cycle()
            await asyncio.sleep(BotConfig.CYCLE_INTERVAL)
    
    async def trading_cycle(self):
        try:
            market_data = self.exchange.get_market_data()
            self.cycle_count += 1

            summary = self.portfolio.get_summary()
            if self.cycle_count % 20 == 0:
                logger.info(f"📊 Cycle #{self.cycle_count} | Value: ${summary['total_value']:,.2f}")

            for symbol in self.symbols:
                if self.portfolio.has_position(symbol):
                    continue  # Skip if position open

                df = self.exchange.get_candles_df(symbol, interval='1m', lookback=BotConfig.MIN_DATA_MINUTES)
                if df.empty:
                    continue

                signal = self.aggregator.aggregate(df, symbol)
                if signal['action'] != 'hold':
                    signal['position_size'] = self.portfolio.calculate_position_size(signal, signal['entry_price'])
                    if self.portfolio.open_position(signal, symbol, signal['entry_price']):
                        logger.info(f"📈 {signal['action']} on {symbol} at {signal['entry_price']:.2f}")
                        if self.telegram.enabled:
                            self.telegram.send_message(
                                f"*Signal*\n"
                                f"Strategy: {signal['strategy']}\n"
                                f"Action: {signal['action'].upper()}\n"
                                f"Symbol: {symbol}\n"
                                f"Confidence: {signal['confidence']:.2f}\n"
                                f"Reason: `{signal['reason']}`"
                            )
        except Exception as e:
            logger.error(f"❌ Trading cycle error: {e}")

    async def stop(self):
        self.is_running = False
        logger.info("🛑 Trading engine stopped")

async def start_bot():
    global GLOBAL_BOT_STATE
    if GLOBAL_BOT_STATE['running']:
        print("⚠️ Bot already running")
        return

    engine = TradingEngine()
    task = asyncio.create_task(engine.start_trading())
    GLOBAL_BOT_STATE.update({
        'engine': engine,
        'task': task,
        'running': True
    })
    print("✅ Bot started in background")

def complete_stop_bot():
    global GLOBAL_BOT_STATE
    if not GLOBAL_BOT_STATE['running']:
        print("⚠️ Bot not running")
        return

    engine = GLOBAL_BOT_STATE['engine']
    asyncio.run(engine.stop())
    GLOBAL_BOT_STATE.update({'engine': None, 'task': None, 'running': False})
    print("🛑 Bot stopped")

def check_status():
    engine = GLOBAL_BOT_STATE['engine']
    if engine:
        summary = engine.portfolio.get_summary()
        print(f"💼 Balance: ${summary['balance']:,.2f}")
        print(f"📈 Total Value: ${summary['total_value']:,.2f}")
        print(f"📊 Open Positions: {summary['open_positions']}")
    else:
        print("❌ Bot not running")

def help_commands():
    print("🧠 Available Commands:")
    print(" • await start_bot() → Start the bot")
    print(" • complete_stop_bot() → Stop the bot")
    print(" • check_status() → View current status")
    print(" • help_commands() → Show this list")
