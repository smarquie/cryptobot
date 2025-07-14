# trading_engine.py

import asyncio
import time
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Local imports
from config import BotConfig
from strategies import UltraScalpStrategy, FastScalpStrategy, QuickMomentumStrategy, TTMSqueezeStrategy
from utils.logger import setup_logger
from utils.ta import TechnicalAnalysis
from utils.telegram import TelegramNotifier
from utils.exchange import CoinbaseExchange

# Setup global logger
setup_logger()
logger = logging.getLogger(__name__)

# Global state
GLOBAL_BOT_STATE = {
    'running': False,
    'engine': None,
    'task': None,
    'stop_requested': False
}

# ==================== POSITION & PORTFOLIO ====================
@dataclass
class Position:
    symbol: str
    side: str  # 'buy' or 'sell'
    size: float
    entry_price: float
    strategy: str
    reason: str
    target_hold: str
    portfolio_summary: Dict
    stop_loss: float = 0.0
    take_profit: float = 0.0
    status: str = 'open'
    entry_time: datetime = datetime.now()
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    fees_paid: float = 0.0

    def __post_init__(self):
        self.fees_paid = self.size * self.entry_price * 0.0002

    def update_price(self, real_current_price: float):
        self.current_price = real_current_price
        if self.side == 'buy':
            self.unrealized_pnl = (real_current_price - self.entry_price) * self.size - self.fees_paid
        else:
            self.unrealized_pnl = (self.entry_price - real_current_price) * self.size - self.fees_paid

    def should_close(self) -> Tuple[bool, str]:
        now = datetime.now()
        hold_time = (now - self.entry_time).total_seconds()
        if hold_time > 600:  # Max 10 minutes
            return True, "max_hold_time"
        if self.side == 'buy' and self.current_price >= self.take_profit:
            return True, "take_profit"
        elif self.side == 'sell' and self.current_price <= self.take_profit:
            return True, "take_profit"
        elif self.side == 'buy' and self.current_price <= self.stop_loss:
            return True, "stop_loss"
        elif self.side == 'sell' and self.current_price >= self.stop_loss:
            return True, "stop_loss"
        return False, 'hold'

    def get_hold_duration(self) -> str:
        duration = datetime.now() - self.entry_time
        total_seconds = int(duration.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}m {seconds}s"

class Portfolio:
    def __init__(self, initial_balance: float = 100000.0):
        self.balance = initial_balance
        self.positions: Dict[str, Position] = {}
        self.trade_history = []

    def open_position(self, signal: Dict, symbol: str, price: float):
        if symbol in self.positions:
            return False
        self.positions[symbol] = Position(**{
            'symbol': symbol,
            'side': signal['action'],
            'size': signal['position_size'],
            'entry_price': price,
            'strategy': signal['strategy'],
            'reason': signal['reason'],
            'target_hold': signal['target_hold'],
            'portfolio_summary': self.get_portfolio_summary(),
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit']
        })
        self.balance -= signal['position_size'] * price
        return True

    def close_position(self, symbol: str, price: float, reason: str = 'manual'):
        if symbol not in self.positions:
            return False
        pos = self.positions.pop(symbol)
        pos.update_price(price)
        realized_pnl = pos.unrealized_pnl
        self.balance += pos.size * price
        self.trade_history.append({
            'symbol': symbol,
            'side': pos.side,
            'size': pos.size,
            'entry_price': pos.entry_price,
            'exit_price': price,
            'pnl': realized_pnl,
            'duration': pos.get_hold_duration(),
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        return True

    def update_positions(self, market_data: Dict[str, float]):
        for symbol, position in self.positions.items():
            if symbol in market_data:
                position.update_price(market_data[symbol])

    def get_portfolio_summary(self) -> Dict:
        total_unrealized_pnl = sum(p.unrealized_pnl for p in self.positions.values())
        total_realized_pnl = sum(t.get('pnl', 0) for t in self.trade_history)
        total_pnl = total_unrealized_pnl + total_realized_pnl
        total_value = self.balance + total_unrealized_pnl
        win_trades = [t for t in self.trade_history if t.get('pnl', 0) > 0]
        win_rate = len(win_trades) / len(self.trade_history) if self.trade_history else 0
        total_exposure = sum(p.size * p.current_price for p in self.positions.values()) / self.balance
        return {
            'initial_balance': self.balance,
            'current_balance': self.balance + total_realized_pnl,
            'total_value': total_value,
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_realized_pnl': total_realized_pnl,
            'total_pnl': total_pnl,
            'win_rate': win_rate,
            'open_positions': len(self.positions),
            'total_exposure_pct': total_exposure * 100,
            'positions': [p.__dict__ for p in self.positions.values()]
        }

    def can_open_position(self, symbol: str, value: float) -> Tuple[bool, str]:
        if len(self.positions) >= BotConfig.MAX_CONCURRENT_POSITIONS:
            return False, "Max positions reached"
        exposure_limit = self.balance * BotConfig.MAX_PORTFOLIO_EXPOSURE
        current_exposure = sum(p.size * p.current_price for p in self.positions.values())
        if (current_exposure + value) > exposure_limit:
            return False, "Portfolio exposure limit exceeded"
        if value > self.balance * BotConfig.MAX_POSITION_PCT:
            return False, "Position size too large"
        return True, "ok"

    def calculate_position_size(self, signal: Dict, price: float) -> float:
        risk_per_unit = abs(price - signal['stop_loss'])
        risk_amount = self.balance * BotConfig.RISK_PER_TRADE
        return risk_amount / risk_per_unit

# ==================== SIGNAL AGGREGATOR ====================
class SignalAggregator:
    def __init__(self):
        self.strategies = {
            'Ultra-Scalp': UltraScalpStrategy(),
            'Fast-Scalp': FastScalpStrategy(),
            'Quick-Momentum': QuickMomentumStrategy(),
            'TTM-Squeeze': TTMSqueezeStrategy()
        }
        self.weights = BotConfig.STRATEGY_WEIGHTS

    def aggregate_signals(self, df: pd.DataFrame, symbol: str) -> Dict:
        signals = []
        for name, strategy in self.strategies.items():
            try:
                signal = strategy.analyze_and_signal(df, symbol)
                if signal['confidence'] >= BotConfig.ULTRA_SCALP_MIN_CONFIDENCE:
                    signal['weighted_confidence'] = signal['confidence'] * self.weights[name]
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Error in {name}: {e}")
        if not signals:
            return {'action': 'hold', 'confidence': 0.0, 'reason': 'No valid signals'}
        best_signal = max(signals, key=lambda x: x['weighted_confidence'])
        return best_signal

# ==================== TRADING ENGINE ====================
class TradingEngine:
    def __init__(self):
        self.config = BotConfig
        self.portfolio = Portfolio(initial_balance=BotConfig.PAPER_INITIAL_BALANCE)
        self.data_client = CoinbaseExchange(
            BotConfig.COINBASE_API_KEY,
            BotConfig.COINBASE_API_SECRET,
            BotConfig.COINBASE_PASSPHRASE
        )
        self.aggregator = SignalAggregator()
        self.telegram = TelegramNotifier(BotConfig.TELEGRAM_BOT_TOKEN, BotConfig.TELEGRAM_CHAT_ID)
        self.is_running = False
        self.cycle_count = 0
        self.start_time = datetime.now()
        self.symbols = BotConfig.TRADING_SYMBOLS

    async def start_trading(self):
        self.is_running = True
        logger.info("🚀 Trading engine started")
        while self.is_running:
            await self.trading_cycle()
            await asyncio.sleep(BotConfig.CYCLE_INTERVAL)

    async def trading_cycle(self):
        try:
            self.cycle_count += 1
            real_market_data = self.data_client.get_market_data()
            self.portfolio.update_positions(real_market_data)

            summary = self.portfolio.get_portfolio_summary()
            if self.cycle_count % 20 == 0:
                logger.info(f"📊 Cycle #{self.cycle_count} | Value: ${summary['total_value']:,.2f} | PnL: ${summary['total_pnl']:,.2f}")

            for symbol in self.symbols:
                if symbol in self.portfolio.positions:
                    continue  # Skip if already in position

                df = self.data_client.get_candles_df(symbol, interval='1m', lookback=BotConfig.MIN_DATA_MINUTES)
                if df.empty:
                    continue

                signal = self.aggregator.aggregate_signals(df, symbol)
                if signal['action'] != 'hold':
                    signal['position_size'] = self.portfolio.calculate_position_size(signal, signal['entry_price'])
                    if self.portfolio.open_position(signal, symbol, signal['entry_price']):
                        logger.info(f"✅ Opened {signal['action']} on {symbol} at {signal['entry_price']:.2f}")
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

# ==================== GLOBAL CONTROL ====================
async def start_bot():
    global GLOBAL_BOT_STATE
    if GLOBAL_BOT_STATE['running']:
        print("⚠️ Bot already running")
        return

    engine = TradingEngine()
    task = asyncio.create_task(engine.start_trading())
    GLOBAL_BOT_STATE.update({'engine': engine, 'task': task, 'running': True})
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
        summary = engine.portfolio.get_portfolio_summary()
        print(f"💼 Balance: ${summary['current_balance']:,.2f}")
        print(f"📈 Total Value: ${summary['total_value']:,.2f}")
        print(f"📊 Open Positions: {summary['open_positions']}")
        print(f"🟢 Win Rate: {summary['win_rate'] * 100:.2f}%")
    else:
        print("❌ Bot not running")

def help_commands():
    print("🧠 Available Commands:")
    print(" • await start_bot() → Start the bot")
    print(" • complete_stop_bot() → Stop the bot")
    print(" • check_status() → View current status")
    print(" • help_commands() → Show this list")
