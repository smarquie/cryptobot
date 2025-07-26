# trading_engine.py

import pandas as pd
import numpy as np
from typing import Dict, Any
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List

# Local imports
from cryptobot.utils.wallet import validate_private_key
from cryptobot.config import BotConfig
from cryptobot.strategies import UltraScalpStrategy, FastScalpStrategy, QuickMomentumStrategy, TTMSqueezeStrategy
from cryptobot.strategies.signal_aggregator import SignalAggregator
from cryptobot.utils.exchange import ExchangeInterface
from cryptobot.utils.telegram import TelegramNotifier
from cryptobot.utils.logger import setup_logger
from cryptobot.utils.portfolio import Portfolio

setup_logger()
logger = logging.getLogger(__name__)

# Global state
GLOBAL_BOT_STATE = {
    'running': False,
    'engine': None,
    'task': None,
    'stop_requested': False
}

class TradingEngine:
    def __init__(self):
        self.config = BotConfig
        self.private_key = BotConfig.HYPERLIQUID_PRIVATE_KEY
        self.wallet = validate_private_key(self.private_key)
        self.exchange = ExchangeInterface(mode=BotConfig.MODE, private_key=self.private_key)
        self.portfolio = Portfolio()
        #self.aggregator = SignalAggregator()
        self.aggregator = SignalAggregator(portfolio=self.portfolio)
        self.telegram = TelegramNotifier()
        self.is_running = False
        self.cycle_count = 0
        self.symbols = BotConfig.TRADING_SYMBOLS
        self.data_collection_start = None
        self.trading_enabled = False
        if self.wallet:
            logger.info(f"✅ Trading wallet loaded: {self.wallet.address}")
        else:
            logger.info("ℹ️ Read-only mode - no valid private key provided")

    async def start_trading(self):
        self.is_running = True
        logger.info("🚀 Trading engine started")
        if BotConfig.DATA_COLLECTION_ENABLED:
            await self.collect_initial_data()
        while self.is_running:
            await self.trading_cycle()
            await asyncio.sleep(BotConfig.CYCLE_INTERVAL)

    async def collect_initial_data(self):
        logger.info(f"📊 Starting {BotConfig.INITIAL_DATA_COLLECTION_MINUTES} minute data collection...")
        self.data_collection_start = datetime.now()
        for minute in range(BotConfig.INITIAL_DATA_COLLECTION_MINUTES):
            if not self.is_running:
                return
            logger.info(f"⏳ Data collection: {minute + 1}/{BotConfig.INITIAL_DATA_COLLECTION_MINUTES} minutes")
            for symbol in self.symbols:
                try:
                    df = self.exchange.get_candles_df(symbol, interval='1m', lookback=BotConfig.MIN_DATA_MINUTES)
                    if not df.empty:
                        logger.info(f"✅ {symbol}: {len(df)} data points collected")
                    else:
                        logger.warning(f"⚠️ {symbol}: No data collected")
                except Exception as e:
                    logger.error(f"❌ {symbol}: Data collection error - {e}")
            await asyncio.sleep(60)
        self.trading_enabled = True
        logger.info("✅ Data collection complete - Trading enabled!")

    async def trading_cycle(self):
        try:
            if not self.trading_enabled and BotConfig.DATA_COLLECTION_ENABLED:
                if self.cycle_count % 10 == 0:
                    elapsed = (datetime.now() - self.data_collection_start).total_seconds() / 60 if self.data_collection_start else 0
                    remaining = max(0, BotConfig.INITIAL_DATA_COLLECTION_MINUTES - elapsed)
                    logger.info(f"📊 Data collection: {elapsed:.1f}/{BotConfig.INITIAL_DATA_COLLECTION_MINUTES} min (remaining: {remaining:.1f})")
                return
            market_data = self._get_multi_timeframe_data()
            self.portfolio.update_current_prices(market_data)
            
            # MONITOR EXISTING POSITIONS FOR EXIT CONDITIONS
            self._check_position_exits(market_data)
            
            self.cycle_count += 1
            summary = self.portfolio.get_summary()
            if self.cycle_count % 5 == 0:
                logger.info(f"📊 Cycle #{self.cycle_count} | Value: ${summary['total_value']:,.2f} | P&L: ${summary['unrealized_pnl']:,.2f}")
                print(f"📊 Cycle #{self.cycle_count} | Value: ${summary['total_value']:,.2f} | P&L: ${summary['unrealized_pnl']:,.2f}")
            for symbol in self.symbols:
                signals = self.aggregator.aggregate(market_data, symbol)
                if not signals:
                    if self.cycle_count % 5 == 0:
                        logger.info(f"📊 {symbol}: No signals from any strategy")
                        print(f"📊 {symbol}: No signals from any strategy")
                    continue
                for signal in signals:
                    can_execute, reason = self.portfolio.can_execute_trade(signal, symbol)
                    if not can_execute:
                        if "Need to close existing" in reason:
                            current_price = market_data.get(symbol, 0)
                            if current_price > 0:
                                logger.info(f"🔄 {symbol}: Direction change detected - closing existing positions")
                                closed_positions = self.portfolio.close_all_positions_for_symbol(symbol, current_price, 'direction_change')
                                if closed_positions:
                                    logger.info(f"✅ {symbol}: Closed {len(closed_positions)} positions, now can execute new trade")
                                    for pos in closed_positions:
                                        portfolio_summary = self.portfolio.get_summary()
                                        hold_duration = "N/A"
                                        if self.telegram.enabled:
                                            self.telegram.send_position_closed(
                                                symbol=symbol,
                                                side=pos['side'],
                                                size=pos['size'],
                                                entry_price=pos.get('entry_price', 0),
                                                close_price=current_price,
                                                pnl=pos['pnl'],
                                                reason='direction_change',
                                                strategy=pos['strategy'],
                                                hold_duration=hold_duration,
                                                portfolio_summary=portfolio_summary
                                            )
                                else:
                                    logger.warning(f"⚠️ {symbol}: Failed to close existing positions")
                                    continue
                            else:
                                logger.warning(f"⚠️ {symbol}: No current price for position closing")
                                continue
                        elif "cooldown" in reason:
                            if self.cycle_count % 5 == 0:
                                logger.info(f"📊 {symbol}: {reason}")
                            continue
                        else:
                            logger.info(f"📊 {symbol}: {reason}")
                            continue
                    if not isinstance(signal, dict):
                        logger.warning(f"⚠️ {symbol}: Invalid signal type {type(signal)} - skipping")
                        continue
                    if signal.get('action') != 'hold':
                        current_price = market_data.get(symbol, signal.get('entry_price', 0))
                        if current_price > 0:
                            position_size = self.portfolio.calculate_position_size(signal, current_price)
                            position_value = position_size * current_price
                            signal_message = (
                                f"🎯 {symbol} Signal: {signal.get('action', 'unknown')} (conf: {signal.get('confidence', 0):.3f})\n"
                                f"📊 Strategy: {signal.get('strategy', 'unknown')} ({signal.get('timeframe', 'unknown')})\n"
                                f"⏰ Timeline: {signal.get('target_hold', 'unknown')}\n"
                                f"💰 Size: {position_size:.6f} {symbol}\n"
                                f"💵 Price: ${current_price:.2f}\n"
                                f"💎 Value: ${position_value:.2f}\n"
                                f"📝 Reason: {signal.get('reason', 'unknown')}"
                            )
                        else:
                            signal_message = (
                                f"🎯 {symbol} Signal: {signal.get('action', 'unknown')} (conf: {signal.get('confidence', 0):.3f})\n"
                                f"📊 Strategy: {signal.get('strategy', 'unknown')} ({signal.get('timeframe', 'unknown')})\n"
                                f"⏰ Timeline: {signal.get('target_hold', 'unknown')}\n"
                                f"📝 Reason: {signal.get('reason', 'unknown')}"
                            )
                        logger.info(signal_message)
                        print(signal_message)
                        if current_price > 0:
                            signal['entry_price'] = current_price
                            signal['position_size'] = position_size
                            if self.portfolio.open_position(signal, symbol, current_price):
                                portfolio_summary = self.portfolio.get_summary()
                                if self.telegram.enabled:
                                    self.telegram.send_position_opened(
                                        symbol=symbol,
                                        side=signal.get('action', 'unknown'),
                                        size=signal.get('position_size', 0),
                                        entry_price=current_price,
                                        strategy=signal.get('strategy', 'unknown'),
                                        reason=signal.get('reason', 'unknown'),
                                        target_hold=signal.get('target_hold', 'unknown'),
                                        portfolio_summary=portfolio_summary
                                    )
        except Exception as e:
            logger.error(f"❌ Trading cycle error: {e}")

    async def stop(self):
        self.is_running = False
        logger.info("🛑 Trading engine stopped")

    def _get_multi_timeframe_data(self) -> Dict:
        market_data = {}
        current_prices = self.exchange.get_market_data()
        market_data.update(current_prices)
        for symbol in self.symbols:
            try:
                df = self.exchange.get_candles_df(symbol, interval='1m', lookback=20)
                if not df.empty:
                    market_data[f"{symbol}_1m"] = df
            except Exception as e:
                logger.warning(f"⚠️ Failed to get 1m data for {symbol}: {e}")
        return market_data

    def _check_position_exits(self, market_data: Dict):
        """Check all open positions for exit conditions (stop loss, take profit, time limit)"""
        current_time = datetime.now()
        
        for (symbol, strategy), position in list(self.portfolio.positions.items()):
            current_price = market_data.get(symbol, position.get('entry_price', 0))
            if current_price <= 0:
                continue
                
            # Check stop loss
            if position.get('stop_loss'):
                if position['side'] == 'buy' and current_price <= position['stop_loss']:
                    logger.info(f"🛑 {symbol} ({strategy}): Stop loss hit at ${current_price:.2f}")
                    self._close_position_with_telegram(symbol, strategy, current_price, 'stop_loss')
                    continue
                elif position['side'] == 'sell' and current_price >= position['stop_loss']:
                    logger.info(f"🛑 {symbol} ({strategy}): Stop loss hit at ${current_price:.2f}")
                    self._close_position_with_telegram(symbol, strategy, current_price, 'stop_loss')
                    continue
            
            # Check take profit
            if position.get('take_profit'):
                if position['side'] == 'buy' and current_price >= position['take_profit']:
                    logger.info(f"💰 {symbol} ({strategy}): Take profit hit at ${current_price:.2f}")
                    self._close_position_with_telegram(symbol, strategy, current_price, 'take_profit')
                    continue
                elif position['side'] == 'sell' and current_price <= position['take_profit']:
                    logger.info(f"💰 {symbol} ({strategy}): Take profit hit at ${current_price:.2f}")
                    self._close_position_with_telegram(symbol, strategy, current_price, 'take_profit')
                    continue
            
            # Check time limit
            if position.get('entry_time'):
                entry_time = datetime.fromisoformat(position['entry_time'])
                max_hold_seconds = position.get('max_hold_time', 1800)  # Default 30 minutes
                elapsed_seconds = (current_time - entry_time).total_seconds()
                
                if elapsed_seconds >= max_hold_seconds:
                    logger.info(f"⏰ {symbol} ({strategy}): Time limit reached ({elapsed_seconds:.0f}s)")
                    self._close_position_with_telegram(symbol, strategy, current_price, 'time_limit')
                    continue

    def _close_position_with_telegram(self, symbol: str, strategy: str, current_price: float, reason: str):
        """Close a position and send Telegram notification"""
        if self.portfolio.close_position(symbol, strategy, current_price, reason):
            # Get the closed position details for Telegram
            portfolio_summary = self.portfolio.get_summary()
            
            # Find the closed position in trade history
            recent_trades = [t for t in self.portfolio.trade_history if t['symbol'] == symbol and t['strategy'] == strategy]
            if recent_trades:
                latest_trade = recent_trades[-1]
                
                # Calculate hold duration
                if 'entry_time' in latest_trade:
                    entry_time = datetime.fromisoformat(latest_trade['entry_time'])
                    hold_duration = f"{((datetime.now() - entry_time).total_seconds() / 60):.1f} minutes"
                else:
                    hold_duration = "N/A"
                
                if self.telegram.enabled:
                    self.telegram.send_position_closed(
                        symbol=symbol,
                        side=latest_trade.get('side', 'unknown'),
                        size=latest_trade.get('size', 0),
                        entry_price=latest_trade.get('entry_price', 0),
                        close_price=current_price,
                        pnl=latest_trade['pnl'],
                        reason=reason,
                        strategy=strategy,
                        hold_duration=hold_duration,
                        portfolio_summary=portfolio_summary
                    )

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

    print(" • complete_stop_bot() → Stop the bot")
    print(" • check_status() → View current status")
    print(" • help_commands() → Show this list")
