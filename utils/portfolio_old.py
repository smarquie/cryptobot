# utils/portfolio.py
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
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
        self.positions = {}  # (symbol, strategy) -> position dict
        self.trade_history = []  # Added missing attribute
        self.data_client = None  # Added missing attribute - you'll need to initialize this properly
        self.current_prices = {}  # Store current market prices
        self.signal_cooldown = {}  # symbol -> last_trade_time
        self.cooldown_minutes = 2  # 2-minute cooling period
        
        # DYNAMIC POSITION SIZING - Can be adjusted while bot runs
        self.dynamic_position_size_percent = BotConfig.POSITION_SIZE_PERCENT
        self.dynamic_min_position_value = BotConfig.MIN_POSITION_VALUE
        self.dynamic_max_position_value = BotConfig.MAX_POSITION_VALUE
        self.dynamic_target_position_value = BotConfig.TARGET_POSITION_VALUE
        
        logger.info(f"💼 Portfolio initialized with ${self.balance:,.2f}")
        logger.info(f"💰 Dynamic position sizing: {self.dynamic_position_size_percent}% (${self.dynamic_target_position_value:,.2f})")
    
    def update_position_sizing(self, 
                             position_size_percent: float = None,
                             min_position_value: float = None,
                             max_position_value: float = None,
                             target_position_value: float = None):
        """
        Update position sizing parameters dynamically while bot runs
        """
        if position_size_percent is not None:
            self.dynamic_position_size_percent = position_size_percent
            logger.info(f"💰 Updated position size percent: {position_size_percent}%")
        
        if min_position_value is not None:
            self.dynamic_min_position_value = min_position_value
            logger.info(f"💰 Updated min position value: ${min_position_value:,.2f}")
        
        if max_position_value is not None:
            self.dynamic_max_position_value = max_position_value
            logger.info(f"💰 Updated max position value: ${max_position_value:,.2f}")
        
        if target_position_value is not None:
            self.dynamic_target_position_value = target_position_value
            logger.info(f"💰 Updated target position value: ${target_position_value:,.2f}")
        
        # Log current sizing
        logger.info(f"💰 Current dynamic sizing: {self.dynamic_position_size_percent}% = ${self.balance * (self.dynamic_position_size_percent / 100):,.2f}")
    
    def get_position_sizing_info(self) -> Dict[str, float]:
        """Get current position sizing parameters"""
        return {
            'position_size_percent': self.dynamic_position_size_percent,
            'min_position_value': self.dynamic_min_position_value,
            'max_position_value': self.dynamic_max_position_value,
            'target_position_value': self.dynamic_target_position_value,
            'current_balance': self.balance,
            'current_target_value': self.balance * (self.dynamic_position_size_percent / 100)
        }
    
    @classmethod
    def update_global_sizing(cls, 
                           position_size_percent: float = None,
                           min_position_value: float = None,
                           max_position_value: float = None,
                           target_position_value: float = None):
        """
        Update global position sizing parameters that will be used by new portfolio instances
        This can be called from Colab cells to change sizing for the entire bot
        """
        if position_size_percent is not None:
            cls.dynamic_position_size_percent = position_size_percent
            print(f"💰 Updated global position size percent: {position_size_percent}%")
        
        if min_position_value is not None:
            cls.dynamic_min_position_value = min_position_value
            print(f"💰 Updated global min position value: ${min_position_value:,.2f}")
        
        if max_position_value is not None:
            cls.dynamic_max_position_value = max_position_value
            print(f"💰 Updated global max position value: ${max_position_value:,.2f}")
        
        if target_position_value is not None:
            cls.dynamic_target_position_value = target_position_value
            print(f"💰 Updated global target position value: ${target_position_value:,.2f}")
        
        print(f"✅ Global position sizing updated successfully!")
    
    @classmethod
    def get_global_sizing_info(cls) -> Dict[str, float]:
        """Get current global position sizing parameters"""
        return {
            'position_size_percent': getattr(cls, 'dynamic_position_size_percent', 25.0),
            'min_position_value': getattr(cls, 'dynamic_min_position_value', 1000.0),
            'max_position_value': getattr(cls, 'dynamic_max_position_value', 3500.0),
            'target_position_value': getattr(cls, 'dynamic_target_position_value', 2500.0)
        }
    
    def has_position(self, symbol: str) -> bool:
        """Check if we have ANY position for a symbol (for backward compatibility)"""
        return any(s == symbol for s, _ in self.positions.keys())
    
    def has_position_for_strategy(self, symbol: str, strategy: str) -> bool:
        """Check if we have a position for a specific symbol and strategy"""
        return (symbol, strategy) in self.positions
    
    def get_position_for_symbol(self, symbol: str) -> Dict:
        """Get the first position for a symbol (for direction checking)"""
        for (s, strategy), pos in self.positions.items():
            if s == symbol:
                return pos
        return None
    
    def is_in_cooldown(self, symbol: str) -> bool:
        """Check if symbol is in cooling period"""
        if symbol not in self.signal_cooldown:
            return False
        
        time_since_last = (datetime.now() - self.signal_cooldown[symbol]).total_seconds() / 60
        return time_since_last < self.cooldown_minutes
    
    def get_cooldown_remaining(self, symbol: str) -> float:
        """Get remaining cooldown time in minutes"""
        if symbol not in self.signal_cooldown:
            return 0.0
        
        time_since_last = (datetime.now() - self.signal_cooldown[symbol]).total_seconds() / 60
        remaining = max(0, self.cooldown_minutes - time_since_last)
        return remaining
    
    def update_current_prices(self, market_data: Dict):
        """Update current market prices for mark-to-market calculations"""
        for symbol, price in market_data.items():
            if isinstance(price, (int, float)) and price > 0:
                self.current_prices[symbol] = price
    
    def calculate_position_size(self, signal: Dict[str, Any], price: float) -> float:
        """Calculate position size based on signal and current price"""
        try:
            # Use DYNAMIC config values for position sizing (can be changed while bot runs)
            target_position_value = self.balance * (self.dynamic_position_size_percent / 100)
            min_position_value = self.dynamic_min_position_value
            max_position_value = self.dynamic_max_position_value
            
            # Calculate position size based on target value
            position_size = target_position_value / price
            
            # Ensure minimum trade size
            min_position_size = min_position_value / price
            position_size = max(position_size, min_position_size)
            
            # Ensure maximum trade size
            max_position_size = max_position_value / price
            position_size = min(position_size, max_position_size)
            
            # Calculate actual position value for logging
            actual_position_value = position_size * price
            
            logger.info(f"💰 Position sizing for {signal.get('symbol', 'unknown')}:")
            logger.info(f"   Target: ${target_position_value:.2f} ({self.dynamic_position_size_percent}% of portfolio)")
            logger.info(f"   Actual: ${actual_position_value:.2f}")
            logger.info(f"   Size: {position_size:.6f} units @ ${price:.2f}")
            
            return position_size
            
        except Exception as e:
            logger.error(f"❌ Error calculating position size: {e}")
            # Fallback to dynamic percentage
            return (self.balance * (self.dynamic_position_size_percent / 100)) / price
    
    def can_execute_trade(self, signal: Dict[str, Any], symbol: str) -> tuple[bool, str]:
        """
        Check if trade can be executed based on cooling period and position logic
        Returns (can_execute, reason)
        """
        action = signal.get('action', 'unknown')
        
        # Check cooling period
        if self.is_in_cooldown(symbol):
            remaining = self.get_cooldown_remaining(symbol)
            return False, f"Symbol in {remaining:.1f}min cooldown"
        
        # Check existing position
        existing_position = self.get_position_for_symbol(symbol)
        if existing_position:
            existing_direction = existing_position['side']
            
            # If same direction, allow trade
            if existing_direction == action:
                return True, "Same direction trade allowed"
            
            # If opposite direction, need to close existing position first
            else:
                return False, f"Need to close existing {existing_direction} position first"
        
        # No existing position, trade allowed
        return True, "No existing position"
    
    def open_position(self, signal: Dict[str, Any], symbol: str, price: float):
        """Open a position based on trading signal"""
        strategy = signal.get('strategy', 'unknown')
        
        # Check if we can execute this trade
        can_execute, reason = self.can_execute_trade(signal, symbol)
        if not can_execute:
            logger.info(f"📊 {symbol}: Cannot execute trade - {reason}")
            return False
        
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
            
            # Store position by symbol AND strategy (FIXED: No more overwriting!)
            self.positions[(symbol, strategy)] = position_data
            
            # Deduct the cost from balance
            position_cost = price * size
            self.balance -= position_cost
            
            # Update cooling period
            self.signal_cooldown[symbol] = datetime.now()
            
            logger.info(f"📈 Opened {signal['action']} on {symbol} with {strategy} strategy")
            logger.info(f"💰 Position cost: ${position_cost:.2f}, New balance: ${self.balance:.2f}")
            logger.info(f"⏰ Cooling period started for {symbol}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to open position: {e}")
            return False
    
    def close_all_positions_for_symbol(self, symbol: str, price: float, reason: str = 'direction_change'):
        """Close all positions for a symbol (for direction change)"""
        closed_positions = []
        
        for (s, strategy) in list(self.positions.keys()):
            if s == symbol:
                pos = self.positions.pop((s, strategy))
                
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
                
                closed_positions.append({
                    'strategy': strategy,
                    'side': pos['side'],
                    'size': pos['size'],
                    'pnl': pnl,
                    'value': position_value
                })
                
                logger.info(f"📉 Closed {pos['side']} on {symbol} ({strategy}) at ${price:.2f}")
                logger.info(f"💰 P&L: ${pnl:.2f}, Position value: ${position_value:.2f}")
        
        if closed_positions:
            total_pnl = sum(p['pnl'] for p in closed_positions)
            total_value = sum(p['value'] for p in closed_positions)
            logger.info(f"📊 Closed {len(closed_positions)} positions for {symbol}")
            logger.info(f"💰 Total P&L: ${total_pnl:.2f}, Total value: ${total_value:.2f}")
            logger.info(f"💼 New balance: ${self.balance:.2f}")
        
        return closed_positions
    
    def close_position(self, symbol: str, strategy: str, price: float, reason: str = 'manual'):
        """Close a specific position by symbol and strategy"""
        if (symbol, strategy) not in self.positions:
            return False
        
        pos = self.positions.pop((symbol, strategy))
        
        # Calculate P&L
        if pos['side'] == 'buy':
            pnl = (price - pos['entry_price']) * pos['size']
        else:  # sell position
            pnl = (pos['entry_price'] - price) * pos['size']
        
        # Add proceeds back to balance
        position_value = price * pos['size']
        self.balance += position_value
        
        # Add to trade history with complete information
        self.trade_history.append({
            'symbol': symbol,
            'strategy': strategy,
            'side': pos['side'],
            'size': pos['size'],
            'entry_price': pos['entry_price'],
            'close_price': price,
            'pnl': pnl,
            'reason': reason,
            'entry_time': pos.get('entry_time'),
            'stop_loss': pos.get('stop_loss'),
            'take_profit': pos.get('take_profit')
        })
        
        logger.info(f"📉 Closed {pos['side']} on {symbol} ({strategy}) at ${price:.2f}")
        logger.info(f"💰 P&L: ${pnl:.2f}, Position value: ${position_value:.2f}, New balance: ${self.balance:.2f}")
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Return portfolio summary with proper mark-to-market calculations and win/loss stats"""
        # Start with cash balance
        total_value = self.balance
        total_unrealized_pnl = 0.0
        
        # Add current market value of all positions
        for (symbol, strategy), pos in self.positions.items():
            current_price = self.current_prices.get(symbol, pos['entry_price'])
            position_value = pos['size'] * current_price
            total_value += position_value
            if pos['side'] == 'buy':
                unrealized_pnl = (current_price - pos['entry_price']) * pos['size']
            else:
                unrealized_pnl = (pos['entry_price'] - current_price) * pos['size']
            total_unrealized_pnl += unrealized_pnl
            if self.positions:
                logger.debug(f"📊 {symbol} ({strategy}): {pos['side']} {pos['size']:.6f} @ ${pos['entry_price']:.2f} → ${current_price:.2f} (P&L: ${unrealized_pnl:.2f})")
        exposure_value = sum(pos['size'] * self.current_prices.get(symbol, pos['entry_price']) for (symbol, strategy), pos in self.positions.items())
        exposure_pct = (exposure_value / total_value * 100) if total_value > 0 else 0.0
        
        # Calculate total return percentage
        initial_balance = BotConfig.INITIAL_BALANCE
        total_return_pct = ((total_value - initial_balance) / initial_balance * 100) if initial_balance > 0 else 0.0
        
        # Win/loss stats - Improved calculation
        total_trades = len(self.trade_history)
        if total_trades > 0:
            # Count winning trades (positive P&L)
            win_trades = [p for p in self.trade_history if p['pnl'] > 0]
            # Count losing trades (negative P&L) 
            loss_trades = [p for p in self.trade_history if p['pnl'] < 0]
            # Count breakeven trades (zero P&L)
            breakeven_trades = [p for p in self.trade_history if p['pnl'] == 0]
            
            # Calculate rates
            win_rate = len(win_trades) / total_trades
            loss_rate = len(loss_trades) / total_trades
            breakeven_rate = len(breakeven_trades) / total_trades
            
            # Calculate averages
            avg_win = sum(p['pnl'] for p in win_trades) / len(win_trades) if win_trades else 0.0
            avg_loss = sum(p['pnl'] for p in loss_trades) / len(loss_trades) if loss_trades else 0.0
            
            logger.info(f"📊 Trade Stats: {len(win_trades)} wins, {len(loss_trades)} losses, {len(breakeven_trades)} breakeven out of {total_trades} total")
            logger.info(f"📊 Win Rate: {win_rate:.1%}, Loss Rate: {loss_rate:.1%}, Breakeven Rate: {breakeven_rate:.1%}")
            
            # Debug: Show recent trades
            if len(self.trade_history) > 0:
                recent_trades = self.trade_history[-5:]  # Last 5 trades
                logger.info(f"📊 Recent trades: {recent_trades}")
        else:
            win_rate = 0.0
            loss_rate = 0.0
            avg_win = 0.0
            avg_loss = 0.0
        return {
            'balance': self.balance,
            'total_value': total_value,
            'open_positions': len(self.positions),
            'unrealized_pnl': total_unrealized_pnl,
            'exposure_pct': exposure_pct,
            'total_return_pct': total_return_pct,
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'trade_count': len(self.trade_history)
        }
