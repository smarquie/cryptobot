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
        self.balance = BotConfig.INITIAL_BALANCE
        self.positions = {}  # symbol -> position dict
        self.strategy_positions = {}  # (symbol, strategy) -> position dict
        self.trade_history = []  # Added missing attribute
        self.data_client = None  # Added missing attribute - you'll need to initialize this properly
        logger.info(f"💼 Portfolio initialized with ${self.balance:,.2f}")
    
    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions
    
    def has_position_for_strategy(self, symbol: str, strategy: str) -> bool:
        """Check if we have a position for a specific symbol and strategy"""
        return (symbol, strategy) in self.strategy_positions
    
    def calculate_position_size(self, signal: Dict[str, Any], price: float) -> float:
        """Calculate position size based on signal and current price"""
        try:
            # Use a simple position sizing strategy
            # Risk 1% of portfolio per trade
            risk_amount = self.balance * 0.01
            
            # Calculate position size based on stop loss
            if 'stop_loss' in signal and signal['stop_loss'] > 0:
                stop_loss_distance = abs(price - signal['stop_loss'])
                if stop_loss_distance > 0:
                    position_size = risk_amount / stop_loss_distance
                else:
                    position_size = risk_amount / (price * 0.01)  # 1% of price as fallback
            else:
                # Default to 1% of portfolio value
                position_size = (self.balance * 0.01) / price
            
            # Ensure position size is reasonable
            max_position = self.balance * 0.1 / price  # Max 10% of portfolio
            position_size = min(position_size, max_position)
            
            return max(0.001, position_size)  # Minimum 0.001
            
        except Exception as e:
            logger.error(f"❌ Error calculating position size: {e}")
            # Fallback to 1% of portfolio
            return (self.balance * 0.01) / price
    
    def open_position(self, signal: Dict[str, Any], symbol: str, price: float):
        """Open a position based on trading signal"""
        strategy = signal.get('strategy', 'unknown')
        
        # Check if we already have a position for this symbol and strategy
        if self.has_position_for_strategy(symbol, strategy):
            logger.info(f"📊 Already have {strategy} position for {symbol} - skipping")
            return False
        
        try:
            size = signal['position_size']
            position_data = {
                'symbol': symbol,
                'side': signal['action'],
                'size': size,
                'entry_price': price,
                'strategy': strategy,
                'entry_time': datetime.now().isoformat(),
                'stop_loss': signal.get('stop_loss'),
                'take_profit': signal.get('take_profit')
            }
            
            # Store position by symbol (for backward compatibility)
            self.positions[symbol] = position_data
            
            # Store position by symbol and strategy (for multi-strategy support)
            self.strategy_positions[(symbol, strategy)] = position_data
            
            self.balance -= price * size
            logger.info(f"📈 Opened {signal['action']} on {symbol} with {strategy} strategy")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to open position: {e}")
            return False
    
    def close_position(self, symbol: str, price: float, reason: str = 'manual'):
        """Close an open position"""
        if symbol not in self.positions:
            return False
        
        pos = self.positions.pop(symbol)
        strategy = pos.get('strategy', 'unknown')
        
        # Remove from strategy positions as well
        if (symbol, strategy) in self.strategy_positions:
            del self.strategy_positions[(symbol, strategy)]
        
        pnl = (price - pos['entry_price']) * pos['size'] if pos['side'] == 'buy' else (pos['entry_price'] - price) * pos['size']
        self.balance += price * pos['size']
        
        # Add to trade history
        self.trade_history.append({
            'symbol': symbol,
            'strategy': strategy,
            'pnl': pnl,
            'reason': reason
        })
        
        logger.info(f"📉 Closed {pos['side']} on {symbol} ({strategy}) at ${price:.2f} | PnL: ${pnl:.2f} ({reason})")
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Return portfolio summary including exposure, PnL, and positions"""
        # Calculate total value (simplified without data_client)
        total_value = self.balance
        for pos in self.positions.values():
            total_value += pos['size'] * pos['entry_price']
        
        # Calculate unrealized PnL (simplified)
        total_unrealized_pnl = 0.0
        for pos in self.positions.values():
            # For now, use entry price as current price (simplified)
            current_price = pos['entry_price']
            if pos['side'] == 'buy':
                total_unrealized_pnl += (current_price - pos['entry_price']) * pos['size']
            else:
                total_unrealized_pnl += (pos['entry_price'] - current_price) * pos['size']
        
        # Calculate exposure percentage
        exposure_value = sum(pos['size'] * pos['entry_price'] for pos in self.positions.values())
        exposure_pct = (exposure_value / total_value * 100) if total_value > 0 else 0.0
        
        # Calculate win rate
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
