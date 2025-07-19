#!/usr/bin/env python3
"""
QUICK-MOMENTUM STRATEGY MODULE
Replacement for GitHub repository - FIXED VERSION
Based on working code with permissive parameters
Includes GCP (Golden Cross Pattern) detection
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base import Strategy
from config import BotConfig
from utils.ta import TechnicalAnalysis

class EarlyGCPDetector:
    """Early Golden Cross Pattern Detector"""
    
    def __init__(self):
        self.name = "GCP-Detector"
    
    def detect_gcp(self, df: pd.DataFrame) -> Dict:
        """Detect Golden Cross Pattern early"""
        try:
            if df.empty or len(df) < 10:
                return {'detected': False, 'confidence': 0.0, 'reason': 'Insufficient data'}
            
            close = df['close']
            
            # Calculate EMAs
            ema_short = self._calculate_ema(close, 5)   # 5-period EMA
            ema_medium = self._calculate_ema(close, 13)  # 13-period EMA
            ema_long = self._calculate_ema(close, 21)    # 21-period EMA
            
            current_price = float(close.iloc[-1])
            current_ema_short = float(ema_short.iloc[-1]) if not pd.isna(ema_short.iloc[-1]) else current_price
            current_ema_medium = float(ema_medium.iloc[-1]) if not pd.isna(ema_medium.iloc[-1]) else current_price
            current_ema_long = float(ema_long.iloc[-1]) if not pd.isna(ema_long.iloc[-1]) else current_price
            
            # Check for Golden Cross Pattern
            short_above_medium = current_ema_short > current_ema_medium
            medium_above_long = current_ema_medium > current_ema_long
            price_above_all = current_price > current_ema_short
            
            # GCP conditions
            gcp_bullish = short_above_medium and medium_above_long and price_above_all
            
            # Calculate momentum
            price_momentum = ((current_price / close.iloc[-3]) - 1) * 100 if len(close) > 2 else 0
            
            confidence = 0.0
            reason = 'No GCP detected'
            
            if gcp_bullish and price_momentum > 0.5:  # FIXED: More permissive
                confidence = min(0.8, 0.5 + (price_momentum / 100))
                reason = f'GCP detected: Short EMA above Medium EMA above Long EMA, momentum={price_momentum:.2f}%'
            
            return {
                'detected': gcp_bullish,
                'confidence': confidence,
                'reason': reason,
                'price_momentum': price_momentum,
                'ema_alignment': short_above_medium and medium_above_long
            }
            
        except Exception as e:
            return {'detected': False, 'confidence': 0.0, 'reason': f'Error: {e}'}
    
    def _calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()

class QuickMomentumStrategy:
    """FIXED Quick-momentum strategy - MUCH MORE PERMISSIVE with GCP detection"""
    
    def __init__(self):
        self.name = "Quick-Momentum"
        self.gcp_detector = EarlyGCPDetector()
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < 10:  # FIXED: Much lower minimum
                return self._empty_signal('Insufficient data')

            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate indicators using centralized parameters
            rsi = self._calculate_rsi(close, 11)  # RSI period
            stoch_k, stoch_d = self._calculate_stochastic(high, low, close, 14)
            macd_line, signal_line, histogram = self._calculate_macd(close, 12, 26, 9)
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            current_stoch_k = float(stoch_k.iloc[-1]) if not pd.isna(stoch_k.iloc[-1]) else 50.0
            current_stoch_d = float(stoch_d.iloc[-1]) if not pd.isna(stoch_d.iloc[-1]) else 50.0
            current_macd = float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else 0.0
            current_signal = float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else 0.0
            
            # GCP Detection
            gcp_result = self.gcp_detector.detect_gcp(df)
            gcp_detected = gcp_result['detected']
            gcp_confidence = gcp_result['confidence']
            
            # RSI Slope calculation
            rsi_slope = 0.0
            if len(rsi) >= 3:
                rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
                rsi_slope = current_rsi - rsi_prev
            
            # MACD momentum
            macd_momentum = 0.0
            if len(histogram) >= 2:
                prev_histogram = float(histogram.iloc[-2]) if not pd.isna(histogram.iloc[-2]) else 0.0
                current_histogram = float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else 0.0
                macd_momentum = current_histogram - prev_histogram
            
            # Price momentum
            price_change_3m = ((current_price / close.iloc[-4]) - 1) * 100 if len(close) > 3 else 0
            
            # Volume analysis
            volume_avg = volume.rolling(7).mean().iloc[-1] if len(volume) >= 7 else volume.iloc[-1]
            volume_surge = float(volume.iloc[-1]) > float(volume_avg) * 1.02  # FIXED: Much lower threshold
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # FIXED BUY SIGNAL - MUCH MORE PERMISSIVE
            if (current_rsi < 50 and  # FIXED: 50 instead of 40
                # FIXED: Much more permissive momentum requirements
                (rsi_slope > -3.0 or price_change_3m > -2.0 or gcp_detected)):  # Either RSI not falling fast OR price not falling fast OR GCP
                
                action = 'buy'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.3  # FIXED: Higher base confidence
                rsi_distance = 50 - current_rsi  # FIXED: Use 50 as threshold
                momentum_bonus = min(0.3, max(0, rsi_slope / 20 + price_change_3m / 100))
                gcp_bonus = gcp_confidence if gcp_detected else 0.0
                volume_bonus = 0.1 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / 30) + momentum_bonus + gcp_bonus + volume_bonus)
                reason = f'FIXED Quick-momentum BUY: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_change_3m:.2f}%'
                if gcp_detected:
                    reason += f', GCP detected'
                
            # FIXED SELL SIGNAL - MUCH MORE PERMISSIVE
            elif (current_rsi > 50 and  # FIXED: 50 instead of 60
                  # FIXED: Much more permissive momentum requirements
                  (rsi_slope < 3.0 or price_change_3m < 2.0)):  # Either RSI not rising fast OR price not rising fast
                
                action = 'sell'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.3  # FIXED: Higher base confidence
                rsi_distance = current_rsi - 50  # FIXED: Use 50 as threshold
                momentum_bonus = min(0.3, max(0, abs(rsi_slope) / 20 + abs(price_change_3m) / 100))
                volume_bonus = 0.1 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / 30) + momentum_bonus + volume_bonus)
                reason = f'FIXED Quick-momentum SELL: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_change_3m:.2f}%'

            # Set stop loss and take profit using centralized parameters
            if action == 'buy':
                stop_loss = current_price * (1 - 0.0040)  # 0.40% stop loss
                take_profit = current_price * (1 + 0.0080)  # 0.80% profit target
            elif action == 'sell':
                stop_loss = current_price * (1 + 0.0040)  # 0.40% stop loss
                take_profit = current_price * (1 - 0.0080)  # 0.80% profit target
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
                'rsi': current_rsi,
                'rsi_slope': rsi_slope,
                'price_change_3m': price_change_3m,
                'gcp_detected': gcp_detected,
                'gcp_confidence': gcp_confidence,
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
            'max_hold_time': 1200,
            'target_hold': '20 minutes'
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
    
    def _calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int):
        """Calculate Stochastic Oscillator"""
        try:
            lowest_low = low.rolling(window=period).min()
            highest_high = high.rolling(window=period).max()
            
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=3).mean()
            
            return k_percent.fillna(50), d_percent.fillna(50)
        except Exception as e:
            return pd.Series([50] * len(close)), pd.Series([50] * len(close))
    
    def _calculate_macd(self, data: pd.Series, fast: int, slow: int, signal: int):
        """Calculate MACD"""
        try:
            ema_fast = self._calculate_ema(data, fast)
            ema_slow = self._calculate_ema(data, slow)
            macd_line = ema_fast - ema_slow
            signal_line = self._calculate_ema(macd_line, signal)
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
        except Exception as e:
            return pd.Series([0] * len(data)), pd.Series([0] * len(data)), pd.Series([0] * len(data))

# Export the strategy classes
__all__ = ['QuickMomentumStrategy', 'EarlyGCPDetector']
