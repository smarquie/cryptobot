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
        self.current_prices = {}  # Store current market prices
        logger.info(f"💼 Portfolio initialized with ${self.balance:,.2f}")
    
    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions
    
    def has_position_for_strategy(self, symbol: str, strategy: str) -> bool:
        """Check if we have a position for a specific symbol and strategy"""
        return (symbol, strategy) in self.strategy_positions
    
    def update_current_prices(self, market_data: Dict):
        """Update current market prices for mark-to-market calculations"""
        for symbol, price in market_data.items():
            if isinstance(price, (int, float)) and price > 0:
                self.current_prices[symbol] = price
    
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
            
            # Deduct the cost from balance
            position_cost = price * size
            self.balance -= position_cost
            
            logger.info(f"📈 Opened {signal['action']} on {symbol} with {strategy} strategy")
            logger.info(f"💰 Position cost: ${position_cost:.2f}, New balance: ${self.balance:.2f}")
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
        
        # Calculate P&L
        if pos['side'] == 'buy':
            pnl = (price - pos['entry_price']) * pos['size']
        else:  # sell position
            pnl = (pos['entry_price'] - price) * pos['size']
        
        # Add proceeds back to balance
        position_value = price * pos['size']
        self.balance += position_value
        
        # Add to trade history
        self.trade_history.append({
            'symbol': symbol,
            'strategy': strategy,
            'pnl': pnl,
            'reason': reason
        })
        
        logger.info(f"📉 Closed {pos['side']} on {symbol} ({strategy}) at ${price:.2f}")
        logger.info(f"💰 P&L: ${pnl:.2f}, Position value: ${position_value:.2f}, New balance: ${self.balance:.2f}")
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Return portfolio summary with proper mark-to-market calculations"""
        # Start with cash balance
        total_value = self.balance
        total_unrealized_pnl = 0.0
        
        # Add current market value of all positions
        for symbol, pos in self.positions.items():
            current_price = self.current_prices.get(symbol, pos['entry_price'])
            
            # Calculate current position value
            position_value = pos['size'] * current_price
            total_value += position_value
            
            # Calculate unrealized P&L
            if pos['side'] == 'buy':
                unrealized_pnl = (current_price - pos['entry_price']) * pos['size']
            else:  # sell position
                unrealized_pnl = (pos['entry_price'] - current_price) * pos['size']
            
            total_unrealized_pnl += unrealized_pnl
            
            # Log position details for debugging
            if self.positions:  # Only log if we have positions
                logger.debug(f"📊 {symbol} ({pos['strategy']}): {pos['side']} {pos['size']:.6f} @ ${pos['entry_price']:.2f} → ${current_price:.2f} (P&L: ${unrealized_pnl:.2f})")
        
        # Calculate exposure percentage
        exposure_value = sum(pos['size'] * self.current_prices.get(symbol, pos['entry_price']) for symbol, pos in self.positions.items())
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
