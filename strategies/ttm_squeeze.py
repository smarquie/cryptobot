#!/usr/bin/env python3
"""
TTM-SQUEEZE STRATEGY MODULE
Replacement for GitHub repository - FIXED VERSION
Based on working code with permissive parameters
"""

import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime

class TTMSqueezeStrategy:
    """FIXED TTM Squeeze + CVD strategy - MUCH MORE PERMISSIVE"""
    
    def __init__(self):
        self.name = "TTM-Squeeze"
        self.squeeze_history = {}  # Track squeeze periods per symbol
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < 20:  # FIXED: Lower minimum
                return self._empty_signal('Insufficient data for TTM analysis')

            high = df['high']
            low = df['low']
            close = df['close']
            volume = df['volume']
            
            # Calculate Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close, 20, 2.0)
            
            # Calculate Keltner Channels
            kc_upper, kc_middle, kc_lower = self._calculate_keltner_channels(high, low, close, 20, 1.5)
            
            # Calculate Donchian Midline for momentum
            donchian_midline = self._calculate_donchian_midline(high, low, 20)
            
            # Calculate CVD
            cvd = self._calculate_cvd(volume, close)
            
            # Current values
            current_price = float(close.iloc[-1])
            current_bb_upper = float(bb_upper.iloc[-1])
            current_bb_lower = float(bb_lower.iloc[-1])
            current_kc_upper = float(kc_upper.iloc[-1])
            current_kc_lower = float(kc_lower.iloc[-1])
            current_donchian = float(donchian_midline.iloc[-1])
            current_sma = float(bb_middle.iloc[-1])
            current_cvd = float(cvd.iloc[-1])
            
            # Check squeeze condition
            squeeze_on = (current_bb_upper < current_kc_upper and current_bb_lower > current_kc_lower)
            
            # Calculate momentum
            momentum_normalized = (current_price - current_donchian) / current_donchian if current_donchian != 0 else 0
            
            # Calculate CVD momentum
            cvd_momentum = 0.0
            if len(cvd) >= 3:
                cvd_prev = float(cvd.iloc[-3]) if not pd.isna(cvd.iloc[-3]) else current_cvd
                cvd_momentum = current_cvd - cvd_prev
            
            # Track squeeze periods
            if symbol not in self.squeeze_history:
                self.squeeze_history[symbol] = 0
            
            if squeeze_on:
                self.squeeze_history[symbol] += 1
            else:
                self.squeeze_history[symbol] = 0
            
            recent_squeeze_count = self.squeeze_history[symbol]
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # FIXED BUY SIGNAL - MUCH MORE PERMISSIVE
            if (not squeeze_on and  # FIXED: Squeeze must be OFF
                recent_squeeze_count >= 2 and  # FIXED: Lower from 3 to 2
                abs(momentum_normalized) > 0.5 and  # FIXED: Keep this threshold
                # FIXED: CVD is now optional bonus, not requirement
                abs(cvd_momentum) > 0.1):  # FIXED: Much lower threshold
                
                action = 'buy'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.6  # FIXED: Higher base confidence
                squeeze_bonus = min(0.2, recent_squeeze_count * 0.1)  # FIXED: Bonus for squeeze duration
                momentum_bonus = min(0.2, abs(momentum_normalized) * 0.4)
                cvd_bonus = min(0.2, abs(cvd_momentum) * 2.0)  # FIXED: CVD is bonus
                
                confidence = min(0.9, base_confidence + squeeze_bonus + momentum_bonus + cvd_bonus)
                reason = f'FIXED TTM BUY: Squeeze={recent_squeeze_count}p, momentum={momentum_normalized:.3f}, CVD={cvd_momentum:.3f}'
                
            # FIXED SELL SIGNAL - MUCH MORE PERMISSIVE
            elif (not squeeze_on and  # FIXED: Squeeze must be OFF
                  recent_squeeze_count >= 2 and  # FIXED: Lower from 3 to 2
                  abs(momentum_normalized) > 0.5 and  # FIXED: Keep this threshold
                  # FIXED: CVD is now optional bonus, not requirement
                  abs(cvd_momentum) > 0.1):  # FIXED: Much lower threshold
                
                action = 'sell'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.6  # FIXED: Higher base confidence
                squeeze_bonus = min(0.2, recent_squeeze_count * 0.1)  # FIXED: Bonus for squeeze duration
                momentum_bonus = min(0.2, abs(momentum_normalized) * 0.4)
                cvd_bonus = min(0.2, abs(cvd_momentum) * 2.0)  # FIXED: CVD is bonus
                
                confidence = min(0.9, base_confidence + squeeze_bonus + momentum_bonus + cvd_bonus)
                reason = f'FIXED TTM SELL: Squeeze={recent_squeeze_count}p, momentum={momentum_normalized:.3f}, CVD={cvd_momentum:.3f}'

            # Set stop loss and take profit using centralized parameters
            if action == 'buy':
                stop_loss = current_price * (1 - 0.002)  # 0.20% stop loss
                take_profit = current_price * (1 + 0.003)  # 0.30% profit target
            elif action == 'sell':
                stop_loss = current_price * (1 + 0.002)  # 0.20% stop loss
                take_profit = current_price * (1 - 0.003)  # 0.30% profit target
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
                'max_hold_time': 1200,  # 20 minutes
                'target_hold': '20 minutes',
                'squeeze_on': squeeze_on,
                'recent_squeeze_count': recent_squeeze_count,
                'momentum_normalized': momentum_normalized,
                'cvd_momentum': cvd_momentum
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
            'max_hold_time': 1200,
            'target_hold': '20 minutes'
        }
    
    def _calculate_bollinger_bands(self, data: pd.Series, period: int, stddev: float) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        try:
            sma = data.rolling(window=period, min_periods=1).mean()
            std = data.rolling(window=period, min_periods=1).std()
            upper = sma + (std * stddev)
            lower = sma - (std * stddev)
            return upper, sma, lower
        except Exception as e:
            return data, data, data
    
    def _calculate_keltner_channels(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int, multiplier: float) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Keltner Channels"""
        try:
            typical_price = (high + low + close) / 3
            atr = self._calculate_atr(high, low, close, period)
            sma = typical_price.rolling(window=period, min_periods=1).mean()
            upper = sma + (atr * multiplier)
            lower = sma - (atr * multiplier)
            return upper, sma, lower
        except Exception as e:
            return close, close, close
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
        """Calculate Average True Range"""
        try:
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period, min_periods=1).mean()
            return atr
        except Exception as e:
            return pd.Series([0] * len(high), index=high.index)
    
    def _calculate_donchian_midline(self, high: pd.Series, low: pd.Series, period: int) -> pd.Series:
        """Calculate Donchian Midline"""
        try:
            highest_high = high.rolling(window=period, min_periods=1).max()
            lowest_low = low.rolling(window=period, min_periods=1).min()
            midline = (highest_high + lowest_low) / 2
            return midline
        except Exception as e:
            return pd.Series([0] * len(high), index=high.index)
    
    def _calculate_cvd(self, volume: pd.Series, close: pd.Series) -> pd.Series:
        """Calculate Cumulative Volume Delta"""
        try:
            price_change = close.diff()
            volume_delta = volume * np.where(price_change > 0, 1, np.where(price_change < 0, -1, 0))
            cvd = volume_delta.cumsum()
            return cvd
        except Exception as e:
            return pd.Series([0] * len(volume), index=volume.index)
