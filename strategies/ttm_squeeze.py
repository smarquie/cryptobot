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

class CompleteTTMSqueezeStrategy:
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
            
            # Track squeeze history
            if symbol not in self.squeeze_history:
                self.squeeze_history[symbol] = []
            
            self.squeeze_history[symbol].append(squeeze_on)
            # Keep only recent history
            if len(self.squeeze_history[symbol]) > 10:
                self.squeeze_history[symbol] = self.squeeze_history[symbol][-10:]
            
            # Calculate momentum
            momentum_delta = current_price - ((current_donchian + current_sma) / 2)
            momentum_normalized = momentum_delta / current_price
            
            # Calculate CVD momentum (rate of change)
            cvd_momentum = 0
            if len(cvd) > 10:  # FIXED: Lower lookback
                cvd_change = current_cvd - float(cvd.iloc[-10])
                cvd_momentum = cvd_change / abs(float(cvd.iloc[-10])) if cvd.iloc[-10] != 0 else 0
            
            # Count consecutive squeeze periods
            recent_squeeze_count = 0
            for i in range(len(self.squeeze_history[symbol]) - 1, -1, -1):
                if self.squeeze_history[symbol][i]:
                    recent_squeeze_count += 1
                else:
                    break
            
            confidence = 0.0
            action = 'hold'
            reason = 'No TTM signal'
            
            # FIXED: Much more permissive entry logic
            if (recent_squeeze_count >= 2 and  # FIXED: Lower threshold from 3
                abs(momentum_normalized) > 0.5):  # FIXED: Removed CVD requirement
                
                # Determine direction
                if momentum_normalized > 0:
                    action = 'buy'
                    reason = f'TTM BUY: Squeeze history, momentum={momentum_normalized:.3f}'
                elif momentum_normalized < 0:
                    action = 'sell'
                    reason = f'TTM SELL: Squeeze history, momentum={momentum_normalized:.3f}'
                
                if action != 'hold':
                    # Calculate confidence
                    confidence = 0.6  # FIXED: Higher base confidence
                    
                    # Bonus for strong squeeze history
                    if recent_squeeze_count >= 3:  # FIXED: Lower threshold
                        confidence += 0.2  # FIXED: Higher bonus
                    
                    # Bonus for strong momentum
                    if abs(momentum_normalized) > 0.5 * 1.5:
                        confidence += 0.1
                    
                    confidence = min(0.95, confidence)

            # Set stop loss and take profit
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
                'squeeze_count': recent_squeeze_count,
                'momentum': momentum_normalized,
                'cvd_momentum': cvd_momentum
            }

        except Exception as e:
            return self._empty_signal(f'TTM Error: {e}')

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
    
    def _fast_sma(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period, min_periods=1).mean()
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
        """Calculate Average True Range"""
        try:
            prev_close = close.shift(1)
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period, min_periods=1).mean()
            
            return atr.fillna(0)
        except Exception as e:
            return pd.Series([0] * len(high), index=high.index)
    
    def _calculate_bollinger_bands(self, data: pd.Series, period: int, std_dev: float):
        """Calculate Bollinger Bands"""
        try:
            sma = self._fast_sma(data, period)
            std = data.rolling(window=period, min_periods=1).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return upper_band, sma, lower_band
        except Exception as e:
            return pd.Series([0] * len(data)), pd.Series([0] * len(data)), pd.Series([0] * len(data))
    
    def _calculate_keltner_channels(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                                   period: int, atr_multiplier: float):
        """Calculate Keltner Channels"""
        try:
            sma = self._fast_sma(close, period)
            atr = self._calculate_atr(high, low, close, period)
            
            upper_channel = sma + (atr * atr_multiplier)
            lower_channel = sma - (atr * atr_multiplier)
            
            return upper_channel, sma, lower_channel
        except Exception as e:
            return pd.Series([0] * len(close)), pd.Series([0] * len(close)), pd.Series([0] * len(close))
    
    def _calculate_donchian_midline(self, high: pd.Series, low: pd.Series, period: int) -> pd.Series:
        """Calculate Donchian Channel Midline"""
        try:
            highest_high = high.rolling(window=period, min_periods=1).max()
            lowest_low = low.rolling(window=period, min_periods=1).min()
            
            midline = (highest_high + lowest_low) / 2
            return midline.fillna(0)
        except Exception as e:
            return pd.Series([0] * len(high), index=high.index)
    
    def _calculate_cvd(self, volume: pd.Series, close: pd.Series) -> pd.Series:
        """Calculate Cumulative Volume Delta (simplified)"""
        try:
            # Simplified CVD: positive volume on up moves, negative on down moves
            price_change = close.diff()
            volume_delta = volume * np.sign(price_change)
            
            # Cumulative sum
            cvd = volume_delta.cumsum()
            return cvd.fillna(0)
        except Exception as e:
            return pd.Series([0] * len(volume), index=volume.index)

# Export the strategy class
__all__ = ['CompleteTTMSqueezeStrategy']
