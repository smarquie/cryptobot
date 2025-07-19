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
        
        # FIXED: Use correct confidence thresholds for each strategy
        valid_signals = []
        for signal in signals:
            strategy_name = signal.get('strategy', 'Unknown')
            
            # Map strategy names to config keys
            strategy_config_map = {
                'Ultra-Scalp': 'ULTRA_SCALP_MIN_CONFIDENCE',
                'Fast-Scalp': 'FAST_SCALP_MIN_CONFIDENCE', 
                'Quick-Momentum': 'QUICK_MOMENTUM_MIN_CONFIDENCE',
                'TTM-Squeeze': 'TTM_SQUEEZE_MIN_CONFIDENCE'
            }
            
            config_key = strategy_config_map.get(strategy_name, 'MIN_CONFIDENCE')
            min_confidence = getattr(BotConfig, config_key, BotConfig.MIN_CONFIDENCE)
            
            if signal['confidence'] >= min_confidence:
                valid_signals.append(signal)
        
        if not valid_signals:
            return {'action': 'hold', 'confidence': 0.0, 'reason': 'No valid signals'}
        
        # FIXED: Use strategy weights properly
        best = max(valid_signals, key=lambda x: x['confidence'] * self.weights.get(x['strategy'], 1.0))
        return best

class TradingEngine:
    def __init__(self):
        self.config = BotConfig
        self.private_key = BotConfig.HYPERLIQUID_PRIVATE_KEY
        self.wallet = validate_private_key(self.private_key)
        self.exchange = ExchangeInterface(mode=BotConfig.MODE, private_key=self.private_key)
        self.portfolio = Portfolio()
        self.aggregator = SignalAggregator()
        self.telegram = TelegramNotifier()
        #    bot_token=BotConfig.TELEGRAM_BOT_TOKEN,
        #    chat_id=BotConfig.TELEGRAM_CHAT_ID
        #)        
        self.is_running = False
        self.cycle_count = 0
        self.symbols = BotConfig.TRADING_SYMBOLS
        
        # FIXED: Add data collection tracking
        self.data_collection_start = None
        self.trading_enabled = False

    async def start_trading(self):
        self.is_running = True
        logger.info("🚀 Trading engine started")
        
        # FIXED: Add data collection phase
        if BotConfig.DATA_COLLECTION_ENABLED:
            await self.collect_initial_data()
        
        while self.is_running:
            await self.trading_cycle()
            await asyncio.sleep(BotConfig.CYCLE_INTERVAL)
    
    async def collect_initial_data(self):
        """Collect initial data before starting trading"""
        logger.info(f"📊 Starting {BotConfig.INITIAL_DATA_COLLECTION_MINUTES} minute data collection...")
        self.data_collection_start = datetime.now()
        
        for minute in range(BotConfig.INITIAL_DATA_COLLECTION_MINUTES):
            if not self.is_running:
                return
            
            logger.info(f"⏳ Data collection: {minute + 1}/{BotConfig.INITIAL_DATA_COLLECTION_MINUTES} minutes")
            
            # Collect data for each symbol
            for symbol in self.symbols:
                try:
                    df = self.exchange.get_candles_df(symbol, interval='1m', lookback=BotConfig.MIN_DATA_MINUTES)
                    if not df.empty:
                        logger.info(f"✅ {symbol}: {len(df)} data points collected")
                    else:
                        logger.warning(f"⚠️ {symbol}: No data collected")
                except Exception as e:
                    logger.error(f"❌ {symbol}: Data collection error - {e}")
            
            await asyncio.sleep(60)  # Wait 1 minute
        
        self.trading_enabled = True
        logger.info("✅ Data collection complete - Trading enabled!")
    
    async def trading_cycle(self):
        try:
            # FIXED: Check if trading is enabled
            if not self.trading_enabled and BotConfig.DATA_COLLECTION_ENABLED:
                if self.cycle_count % 10 == 0:  # Log every 10 cycles
                    elapsed = (datetime.now() - self.data_collection_start).total_seconds() / 60 if self.data_collection_start else 0
                    remaining = max(0, BotConfig.INITIAL_DATA_COLLECTION_MINUTES - elapsed)
                    logger.info(f"📊 Data collection: {elapsed:.1f}/{BotConfig.INITIAL_DATA_COLLECTION_MINUTES} min (remaining: {remaining:.1f})")
                return
            
            # Get market data for all timeframes
            market_data = self._get_multi_timeframe_data()
            self.cycle_count += 1

            summary = self.portfolio.get_summary()
            if self.cycle_count % 5 == 0:  # Log every 5 cycles instead of 20
                logger.info(f"📊 Cycle #{self.cycle_count} | Value: ${summary['total_value']:,.2f}")
                print(f"📊 Cycle #{self.cycle_count} | Value: ${summary['total_value']:,.2f}")

            # Process each symbol for multiple strategies
            for symbol in self.symbols:
                # Get all signals from all strategies for this symbol
                signals = self.aggregator.aggregate(market_data, symbol)
                
                if not signals:
                    # Log why no signals were generated (every 5 cycles)
                    if self.cycle_count % 5 == 0:
                        logger.info(f"📊 {symbol}: No signals from any strategy")
                        print(f"📊 {symbol}: No signals from any strategy")
                    continue
                
                # Process each signal from different strategies
                for signal in signals:
                    # Skip if we already have a position for this symbol (for now)
                    # TODO: Allow multiple positions per symbol with different strategies
                    if self.portfolio.has_position(symbol):
                        continue
                    
                    # Enhanced logging with timeline information
                    if signal['action'] != 'hold':
                        current_price = market_data.get(symbol, signal.get('entry_price', 0))
                        if current_price > 0:
                            position_size = self.portfolio.calculate_position_size(signal, current_price)
                            position_value = position_size * current_price
                            
                            signal_message = (
                                f"🎯 {symbol} Signal: {signal['action']} (conf: {signal['confidence']:.3f})\n"
                                f"📊 Strategy: {signal['strategy']} ({signal['timeframe']})\n"
                                f"⏰ Timeline: {signal['target_hold']}\n"
                                f"💰 Size: {position_size:.6f} {symbol}\n"
                                f"💵 Price: ${current_price:.2f}\n"
                                f"💎 Value: ${position_value:.2f}\n"
                                f"📝 Reason: {signal['reason']}"
                            )
                        else:
                            signal_message = (
                                f"🎯 {symbol} Signal: {signal['action']} (conf: {signal['confidence']:.3f})\n"
                                f"📊 Strategy: {signal['strategy']} ({signal['timeframe']})\n"
                                f"⏰ Timeline: {signal['target_hold']}\n"
                                f"📝 Reason: {signal['reason']}"
                            )
                        
                        logger.info(signal_message)
                        print(signal_message)
                        
                        # Execute trade if valid
                        if current_price > 0:
                            signal['entry_price'] = current_price
                            signal['position_size'] = position_size
                            
                            if self.portfolio.open_position(signal, symbol, current_price):
                                # Enhanced trade execution message with timeline
                                portfolio_summary = self.portfolio.get_summary()
                                
                                trade_message = (
                                    f"📈 {signal['action'].upper()} {symbol}\n"
                                    f"📊 Strategy: {signal['strategy']} ({signal['timeframe']})\n"
                                    f"⏰ Timeline: {signal['target_hold']}\n"
                                    f"💰 Size: {signal['position_size']:.6f} {symbol}\n"
                                    f"💵 Entry: ${current_price:.2f}\n"
                                    f"💎 Value: ${position_value:.2f}\n"
                                    f"📊 Confidence: {signal['confidence']:.3f}\n"
                                    f"📝 Reason: {signal['reason']}\n"
                                    f"💼 Portfolio: ${portfolio_summary['total_value']:,.2f}"
                                )
                                
                                logger.info(trade_message)
                                print(trade_message)
                                
                                if self.telegram.enabled:
                                    self.telegram.send_message(
                                        f"*TRADE EXECUTED*\n"
                                        f"📈 {signal['action'].upper()} {symbol}\n"
                                        f"📊 Strategy: {signal['strategy']} ({signal['timeframe']})\n"
                                        f"⏰ Timeline: {signal['target_hold']}\n"
                                        f"💰 Size: {signal['position_size']:.6f} {symbol}\n"
                                        f"💵 Entry: ${current_price:.2f}\n"
                                        f"💎 Value: ${position_value:.2f}\n"
                                        f"📊 Confidence: {signal['confidence']:.3f}\n"
                                        f"📝 Reason: `{signal['reason']}`\n"
                                        f"💼 Portfolio: ${portfolio_summary['total_value']:,.2f}"
                                    )
        except Exception as e:
            logger.error(f"❌ Trading cycle error: {e}")

    def _get_multi_timeframe_data(self) -> Dict:
        """Get market data for all timeframes needed by strategies"""
        market_data = {}
        
        # Get current market prices
        current_prices = self.exchange.get_market_data()
        market_data.update(current_prices)
        
        # Get timeframe-specific data for each symbol
        timeframes = ['1m', '5m', '15m', '1h']
        
        for symbol in self.symbols:
            for timeframe in timeframes:
                try:
                    # Get appropriate lookback based on timeframe
                    lookback_map = {
                        '1m': 10,
                        '5m': 20, 
                        '15m': 40,
                        '1h': 24
                    }
                    lookback = lookback_map.get(timeframe, 20)
                    
                    df = self.exchange.get_candles_df(symbol, interval=timeframe, lookback=lookback)
                    if not df.empty:
                        market_data[f"{symbol}_{timeframe}"] = df
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to get {timeframe} data for {symbol}: {e}")
        
        return market_data

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
        print(f"🔄 Trading Enabled: {engine.trading_enabled}")
        print(f"📊 Cycle Count: {engine.cycle_count}")
    else:
        print("❌ Bot not running")

def help_commands():
    print("🧠 Available Commands:")
    print(" • await start_bot() → Start the bot")
    print(" • complete_stop_bot() → Stop the bot")
    print(" • check_status() → View current status")
    print(" • help_commands() → Show this list")
