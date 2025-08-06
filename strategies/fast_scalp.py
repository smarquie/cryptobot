#!/usr/bin/env python3
"""
FAST-SCALP STRATEGY MODULE - CENTRALIZED VERSION
All parameters moved to config.py for centralized management
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from cryptobot.config import BotConfig

class FastScalpStrategy:
    """Fast-scalp strategy using centralized parameters from config"""
    
    def __init__(self):
        self.name = "Fast-Scalp"
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < BotConfig.MIN_DATA_POINTS:
                return self._empty_signal('Insufficient data')
    
            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate indicators using config parameters
            rsi = self._calculate_rsi(close, BotConfig.FAST_SCALP_RSI_PERIOD)
            macd, macd_signal, macd_hist = self._calculate_macd(
                close, 
                BotConfig.FAST_SCALP_MACD_FAST, 
                BotConfig.FAST_SCALP_MACD_SLOW, 
                BotConfig.FAST_SCALP_MACD_SIGNAL
            )
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            current_macd = float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else 0.0
            current_macd_signal = float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else 0.0
            
            # Volume analysis using config parameters
            volume_avg = volume.rolling(BotConfig.FAST_SCALP_VOLUME_AVERAGE_PERIOD).mean().iloc[-1] if len(volume) >= BotConfig.FAST_SCALP_VOLUME_AVERAGE_PERIOD else volume.iloc[-1]
            volume_surge = float(volume.iloc[-1]) > float(volume_avg) * BotConfig.FAST_SCALP_VOLUME_SURGE_MULTIPLIER
            
            # RSI momentum check instead of price change
            rsi_series = rsi.dropna()
            rsi_momentum_up = False
            rsi_momentum_down = False

            # Replace MACD with EMA crossover
            ema_fast = close.ewm(span=BotConfig.FAST_SCALP_EMA_FAST, adjust=False).mean()
            ema_slow = close.ewm(span=BotConfig.FAST_SCALP_EMA_SLOW, adjust=False).mean()
            
            if len(rsi_series) >= 2:  # Need at least 2 periods for momentum
                # Get current and previous RSI values
                current_rsi_val = rsi_series.iloc[-1]
                prev_rsi_val = rsi_series.iloc[-2]  # Previous candle's RSI
                
                # Check RSI momentum direction
                rsi_momentum_up = current_rsi_val > prev_rsi_val
                rsi_momentum_down = current_rsi_val < prev_rsi_val
    
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # BUY SIGNAL using RSI momentum instead of price change
            if (current_rsi < BotConfig.FAST_SCALP_RSI_OVERSOLD and
                ema_fast.iloc[-1] > ema_slow.iloc[-1] and 
                #current_macd > current_macd_signal and  # MACD bullish crossover
                rsi_momentum_up):  # RSI showing upward momentum
                
                action = 'buy'
                
                # Confidence calculation using config parameters
                base_confidence = BotConfig.FAST_SCALP_BASE_CONFIDENCE
                rsi_bonus = max(0, (BotConfig.FAST_SCALP_RSI_OVERSOLD - current_rsi) / BotConfig.FAST_SCALP_RSI_DISTANCE_DIVISOR)
                macd_bonus = min(BotConfig.FAST_SCALP_MACD_BONUS_MAX, max(0, (current_macd - current_macd_signal) / 100))
                volume_bonus = BotConfig.FAST_SCALP_VOLUME_BONUS if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + rsi_bonus + macd_bonus + volume_bonus)
                reason = f'Fast-scalp BUY: RSI={current_rsi:.1f} (↑), MACD={current_macd:.4f}'
                
            # SELL SIGNAL using RSI momentum instead of price change
            elif (current_rsi > BotConfig.FAST_SCALP_RSI_OVERBOUGHT and
                  current_macd < current_macd_signal and  # MACD bearish crossover
                  rsi_momentum_down):  # RSI showing downward momentum
                
                action = 'sell'
                
                # Confidence calculation using config parameters
                base_confidence = BotConfig.FAST_SCALP_BASE_CONFIDENCE
                rsi_bonus = max(0, (current_rsi - BotConfig.FAST_SCALP_RSI_OVERBOUGHT) / BotConfig.FAST_SCALP_RSI_DISTANCE_DIVISOR)
                macd_bonus = min(BotConfig.FAST_SCALP_MACD_BONUS_MAX, max(0, (current_macd_signal - current_macd) / 100))
                volume_bonus = BotConfig.FAST_SCALP_VOLUME_BONUS if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + rsi_bonus + macd_bonus + volume_bonus)
                reason = f'Fast-scalp SELL: RSI={current_rsi:.1f} (↓), MACD={current_macd:.4f}'
    
            # Set stop loss and take profit using config parameters
            if action == 'buy':
                stop_loss = current_price * (1 - BotConfig.FAST_SCALP_STOP_LOSS_PERCENT)
                take_profit = current_price * (1 + BotConfig.FAST_SCALP_TAKE_PROFIT_PERCENT)
            elif action == 'sell':
                stop_loss = current_price * (1 + BotConfig.FAST_SCALP_STOP_LOSS_PERCENT)
                take_profit = current_price * (1 - BotConfig.FAST_SCALP_TAKE_PROFIT_PERCENT)
            else:
                stop_loss = current_price
                take_profit = current_price
    
            return {
                'action': action,
                'confidence': confidence,
                'strategy': self.name,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'reason': reason,
                'max_hold_time': BotConfig.FAST_SCALP_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.FAST_SCALP_MAX_HOLD_SECONDS // 60} minutes',
                'rsi': current_rsi,
                'macd': current_macd,
                'macd_signal': current_macd_signal,
                'rsi_momentum': 'up' if rsi_momentum_up else 'down' if rsi_momentum_down else 'flat'
            }
    
        except Exception as e:
            return self._empty_signal(f'Error: {e}')

    
    def _empty_signal(self, reason: str) -> Dict:
        return {
            'action': 'hold',
            'confidence': 0.0,
            'strategy': self.name,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'reason': reason,
            'max_hold_time': BotConfig.FAST_SCALP_MAX_HOLD_SECONDS,
            'target_hold': f'{BotConfig.FAST_SCALP_MAX_HOLD_SECONDS // 60} minutes'
        }
    
    def _calculate_rsi(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate RSI"""
        try:
            delta = data.diff()
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            
            avg_gains = gains.ewm(span=period, adjust=False).mean()
            avg_losses = losses.ewm(span=period, adjust=False).mean()
            
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.fillna(50)
        except Exception as e:
            return pd.Series([50] * len(data), index=data.index)
    
    def _calculate_macd(self, data: pd.Series, fast: int, slow: int, signal: int) -> tuple:
        """Calculate MACD"""
        try:
            ema_fast = data.ewm(span=fast, adjust=False).mean()
            ema_slow = data.ewm(span=slow, adjust=False).mean()
            macd = ema_fast - ema_slow
            macd_signal = macd.ewm(span=signal, adjust=False).mean()
            macd_hist = macd - macd_signal
            
            return macd, macd_signal, macd_hist
        except Exception as e:
            zeros = pd.Series([0] * len(data), index=data.index)
            return zeros, zeros, zeros

# Export the strategy class
__all__ = ['FastScalpStrategy']
