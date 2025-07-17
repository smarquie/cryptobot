#!/usr/bin/env python3
"""
TTM-SQUEEZE STRATEGY MODULE
Replacement for GitHub repository - FIXED VERSION
Based on working code with permissive parameters
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base import Strategy
from config import BotConfig
from utils.ta import TechnicalAnalysis

class TTMSqueezeStrategy:
    """FIXED TTM-Squeeze strategy - MUCH MORE PERMISSIVE"""
    
    def __init__(self):
        self.name = "TTM-Squeeze"
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < 12:  # FIXED: Much lower minimum
                return self._empty_signal('Insufficient data')

            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate indicators using centralized parameters
            rsi = self._calculate_rsi(close, 14)  # RSI period
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close, 20, 2)
            keltner_upper, keltner_middle, keltner_lower = self._calculate_keltner_channels(high, low, close, 20, 1.5)
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            current_bb_upper = float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else current_price * 1.02
            current_bb_lower = float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else current_price * 0.98
            current_keltner_upper = float(keltner_upper.iloc[-1]) if not pd.isna(keltner_upper.iloc[-1]) else current_price * 1.02
            current_keltner_lower = float(keltner_lower.iloc[-1]) if not pd.isna(keltner_lower.iloc[-1]) else current_price * 0.98
            
            # Squeeze detection
            bb_width = current_bb_upper - current_bb_lower
            keltner_width = current_keltner_upper - current_keltner_lower
            squeeze_on = bb_width < keltner_width
            
            # Momentum indicators
            rsi_slope = 0.0
            if len(rsi) >= 3:
                rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
                rsi_slope = current_rsi - rsi_prev
            
            # Price momentum
            price_change_5m = ((current_price / close.iloc[-6]) - 1) * 100 if len(close) > 5 else 0
            
            # Volume analysis
            volume_avg = volume.rolling(10).mean().iloc[-1] if len(volume) >= 10 else volume.iloc[-1]
            volume_surge = float(volume.iloc[-1]) > float(volume_avg) * 1.01  # FIXED: Much lower threshold
            
            # Position relative to bands
            bb_position = (current_price - current_bb_lower) / (current_bb_upper - current_bb_lower) if (current_bb_upper - current_bb_lower) > 0 else 0.5
            keltner_position = (current_price - current_keltner_lower) / (current_keltner_upper - current_keltner_lower) if (current_keltner_upper - current_keltner_lower) > 0 else 0.5
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # FIXED BUY SIGNAL - MUCH MORE PERMISSIVE
            if (current_rsi < 55 and  # FIXED: 55 instead of 45
                # FIXED: Much more permissive squeeze requirements
                (squeeze_on or bb_position < 0.7) and  # Either in squeeze OR not at upper BB
                # FIXED: Much more permissive momentum requirements
                (rsi_slope > -2.0 or price_change_5m > -1.5)):  # Either RSI not falling fast OR price not falling fast
                
                action = 'buy'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.4  # FIXED: Higher base confidence
                rsi_distance = 55 - current_rsi  # FIXED: Use 55 as threshold
                squeeze_bonus = 0.2 if squeeze_on else 0.1
                momentum_bonus = min(0.2, max(0, rsi_slope / 15 + price_change_5m / 100))
                volume_bonus = 0.1 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / 30) + squeeze_bonus + momentum_bonus + volume_bonus)
                reason = f'FIXED TTM-Squeeze BUY: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), squeeze={squeeze_on}, momentum={price_change_5m:.2f}%'
                
            # FIXED SELL SIGNAL - MUCH MORE PERMISSIVE
            elif (current_rsi > 45 and  # FIXED: 45 instead of 55
                  # FIXED: Much more permissive squeeze requirements
                  (squeeze_on or bb_position > 0.3) and  # Either in squeeze OR not at lower BB
                  # FIXED: Much more permissive momentum requirements
                  (rsi_slope < 2.0 or price_change_5m < 1.5)):  # Either RSI not rising fast OR price not rising fast
                
                action = 'sell'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.4  # FIXED: Higher base confidence
                rsi_distance = current_rsi - 45  # FIXED: Use 45 as threshold
                squeeze_bonus = 0.2 if squeeze_on else 0.1
                momentum_bonus = min(0.2, max(0, abs(rsi_slope) / 15 + abs(price_change_5m) / 100))
                volume_bonus = 0.1 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / 30) + squeeze_bonus + momentum_bonus + volume_bonus)
                reason = f'FIXED TTM-Squeeze SELL: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), squeeze={squeeze_on}, momentum={price_change_5m:.2f}%'

            # Set stop loss and take profit using centralized parameters
            if action == 'buy':
                stop_loss = current_price * (1 - 0.0050)  # 0.50% stop loss
                take_profit = current_price * (1 + 0.0100)  # 1.00% profit target
            elif action == 'sell':
                stop_loss = current_price * (1 + 0.0050)  # 0.50% stop loss
                take_profit = current_price * (1 - 0.0100)  # 1.00% profit target
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
                'max_hold_time': 1800,  # 30 minutes
                'target_hold': '30 minutes',
                'rsi': current_rsi,
                'rsi_slope': rsi_slope,
                'price_change_5m': price_change_5m,
                'squeeze_on': squeeze_on,
                'bb_position': bb_position,
                'keltner_position': keltner_position,
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
            'max_hold_time': 1800,
            'target_hold': '30 minutes'
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
    
    def _calculate_bollinger_bands(self, data: pd.Series, period: int, std_dev: float):
        """Calculate Bollinger Bands"""
        try:
            sma = data.rolling(window=period).mean()
            std = data.rolling(window=period).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return upper_band.fillna(data), sma.fillna(data), lower_band.fillna(data)
        except Exception as e:
            return data * 1.02, data, data * 0.98
    
    def _calculate_keltner_channels(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int, multiplier: float):
        """Calculate Keltner Channels"""
        try:
            typical_price = (high + low + close) / 3
            atr = self._calculate_atr(high, low, close, period)
            
            middle = typical_price.rolling(window=period).mean()
            upper = middle + (atr * multiplier)
            lower = middle - (atr * multiplier)
            
            return upper.fillna(close), middle.fillna(close), lower.fillna(close)
        except Exception as e:
            return close * 1.02, close, close * 0.98
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
        """Calculate Average True Range"""
        try:
            high_low = high - low
            high_close = np.abs(high - close.shift())
            low_close = np.abs(low - close.shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            
            return atr.fillna(high_low.mean())
        except Exception as e:
            return pd.Series([0.01] * len(high), index=high.index)

# Export the strategy class
__all__ = ['TTMSqueezeStrategy']
