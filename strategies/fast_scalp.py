#!/usr/bin/env python3
"""
FAST-SCALP STRATEGY MODULE
Replacement for GitHub repository - FIXED VERSION
Based on working code with permissive parameters
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class FastScalpStrategy:
    """FIXED Fast-scalp strategy - MUCH MORE PERMISSIVE"""
    
    def __init__(self):
        self.name = "Fast-Scalp"
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < 8:  # FIXED: Much lower minimum
                return self._empty_signal('Insufficient data')

            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate indicators using centralized parameters
            rsi = self._calculate_rsi(close, 9)  # RSI period
            ema_fast = self._calculate_ema(close, 8)  # Fast EMA
            ema_slow = self._calculate_ema(close, 21)  # Slow EMA
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            current_ema_fast = float(ema_fast.iloc[-1]) if not pd.isna(ema_fast.iloc[-1]) else current_price
            current_ema_slow = float(ema_slow.iloc[-1]) if not pd.isna(ema_slow.iloc[-1]) else current_price
            
            # EMA crossover
            ema_crossover = current_ema_fast > current_ema_slow
            
            # RSI Slope calculation
            rsi_slope = 0.0
            if len(rsi) >= 3:
                rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
                rsi_slope = current_rsi - rsi_prev
            
            # Price momentum
            price_change_2m = ((current_price / close.iloc[-3]) - 1) * 100 if len(close) > 2 else 0
            
            # Volume analysis
            volume_avg = volume.rolling(5).mean().iloc[-1] if len(volume) >= 5 else volume.iloc[-1]
            volume_surge = float(volume.iloc[-1]) > float(volume_avg) * 1.05  # FIXED: Lower threshold
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # FIXED BUY SIGNAL - MUCH MORE PERMISSIVE
            if (current_rsi < 45 and  # FIXED: 45 instead of 35
                ema_crossover and  # EMA crossover required
                # FIXED: Much more permissive momentum requirements
                (rsi_slope > -2.0 or price_change_2m > -1.0)):  # Either RSI not falling fast OR price not falling fast
                
                action = 'buy'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.4  # FIXED: Higher base confidence
                rsi_distance = 45 - current_rsi  # FIXED: Use 45 as threshold
                momentum_bonus = min(0.3, max(0, rsi_slope / 15 + price_change_2m / 50))
                volume_bonus = 0.1 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / 25) + momentum_bonus + volume_bonus)
                reason = f'FIXED Fast-scalp BUY: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), EMA crossover, momentum={price_change_2m:.2f}%'
                
            # FIXED SELL SIGNAL - MUCH MORE PERMISSIVE
            elif (current_rsi > 55 and  # FIXED: 55 instead of 65
                  not ema_crossover and  # EMA crossover required
                  # FIXED: Much more permissive momentum requirements
                  (rsi_slope < 2.0 or price_change_2m < 1.0)):  # Either RSI not rising fast OR price not rising fast
                
                action = 'sell'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.4  # FIXED: Higher base confidence
                rsi_distance = current_rsi - 55  # FIXED: Use 55 as threshold
                momentum_bonus = min(0.3, max(0, abs(rsi_slope) / 15 + abs(price_change_2m) / 50))
                volume_bonus = 0.1 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / 25) + momentum_bonus + volume_bonus)
                reason = f'FIXED Fast-scalp SELL: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), EMA crossover, momentum={price_change_2m:.2f}%'

            # Set stop loss and take profit using centralized parameters
            if action == 'buy':
                stop_loss = current_price * (1 - 0.0030)  # 0.30% stop loss
                take_profit = current_price * (1 + 0.0060)  # 0.60% profit target
            elif action == 'sell':
                stop_loss = current_price * (1 + 0.0030)  # 0.30% stop loss
                take_profit = current_price * (1 - 0.0060)  # 0.60% profit target
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
                'max_hold_time': 900,  # 15 minutes
                'target_hold': '15 minutes',
                'rsi': current_rsi,
                'rsi_slope': rsi_slope,
                'price_change_2m': price_change_2m,
                'ema_crossover': ema_crossover,
                'volume_surge': volume_surge
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
            'max_hold_time': 900,
            'target_hold': '15 minutes'
        }
    
    def _calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
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

# Export the strategy class
__all__ = ['FastScalpStrategy']
