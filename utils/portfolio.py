# utils/portfolio.py
import logging
from typing import Dict, Any
from datetime import datetime
from config import BotConfig

logger = logging.getLogger(__name__)

class Position:
    def __init__(self, symbol: str, side: str, size: float, entry_price: float, strategy: str):
        self.symbol = symbol
        self.side = side
        self.size = size
        self.entry_price = entry_price
        self.strategy = strategy
        self.unrealized_pnl = 0.0
        self.realized_pnl = 0.0
    
    def update_price(self, current_price: float):
        if self.side == 'buy':
            self.unrealized_pnl = (current_price - self.entry_price) * self.size
        else:
            self.unrealized_pnl = (self.entry_price - current_price) * self.size

class Portfolio:
    def __init__(self):
        self.balance = BotConfig.PAPER_INITIAL_BALANCE
        self.positions = {}
        self.trade_history = []  # Added missing attribute
        self.data_client = None  # Added missing attribute - you'll need to initialize this properly
        logger.info(f"💼 Portfolio initialized with ${self.balance:,.2f}")
    
    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions
    
    def open_position(self, signal: Dict[str, Any], symbol: str, price: float):
        """Open a position based on trading signal"""
        if self.has_position(symbol):
            return False
        
        try:
            size = signal['position_size']
            self.positions[symbol] = {
                'symbol': symbol,
                'side': signal['action'],
                'size': size,
                'entry_price': price,
                'strategy': signal['strategy'],
                'entry_time': datetime.now().isoformat(),
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit']
            }
            self.balance -= price * size
            logger.info(f"📈 Opened {signal['action']} on {symbol}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to open position: {e}")
            return False
    
    def close_position(self, symbol: str, price: float, reason: str = 'manual'):
        """Close an open position"""
        if symbol not in self.positions:
            return False
        
        pos = self.positions.pop(symbol)
        pnl = (price - pos['entry_price']) * pos['size'] if pos['side'] == 'buy' else (pos['entry_price'] - price) * pos['size']
        self.balance += price * pos['size']
        
        # Add to trade history
        self.trade_history.append({
            'symbol': symbol,
            'pnl': pnl,
            'reason': reason
        })
        
        logger.info(f"📉 Closed {pos['side']} on {symbol} at ${price:.2f} | PnL: ${pnl:.2f} ({reason})")
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Return portfolio summary including exposure, PnL, and positions"""
        total_value = self.balance + sum(
            pos['size'] * self.data_client.get_market_data().get(pos['symbol'], pos['entry_price']) 
            for pos in self.positions.values()
        )
        
        total_unrealized_pnl = 0.0
        for pos in self.positions.values():
            current_price = self.data_client.get_market_data().get(pos['symbol'], pos['entry_price'])
            if pos['side'] == 'buy':
                total_unrealized_pnl += (current_price - pos['entry_price']) * pos['size']
            else:
                total_unrealized_pnl += (pos['entry_price'] - current_price) * pos['size']
        
        exposure_pct = (sum(
            pos['size'] * self.data_client.get_market_data().get(pos['symbol'], pos['entry_price']) 
            for pos in self.positions.values()
        ) / total_value * 100) if total_value > 0 else 0.0
        
        win_trades = [p for p in self.trade_history if p['pnl'] > 0]
        win_rate = len(win_trades) / len(self.trade_history) if self.trade_history else 0.0
        
        return {
            'balance': self.balance,
            'total_value': total_value,
            'open_positions': len(self.positions),
            'unrealized_pnl': total_unrealized_pnl,
            'exposure_pct': exposure_pct,
            'win_rate': win_rate,
            'trade_count': len(self.trade_history)
        }
