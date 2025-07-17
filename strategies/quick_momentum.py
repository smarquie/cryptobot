#!/usr/bin/env python3
"""
QUICK-MOMENTUM STRATEGY MODULE
Replacement for GitHub repository - FIXED VERSION
Based on working code with GCP pattern detection
"""

import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime

class CompleteQuickMomentumStrategy:
    """FIXED Quick-momentum strategy with GCP detection - MUCH MORE PERMISSIVE"""
    
    def __init__(self):
        self.name = "Quick-Momentum"
        self.gcp_detector = EarlyGCPDetector()
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < 15:  # FIXED: Much lower minimum
                return self._empty_signal('Insufficient data')

            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate indicators using centralized parameters
            rsi = self._calculate_rsi(close, 7)  # RSI period
            sma_fast = self._fast_sma(close, 3)  # Fast MA
            sma_slow = self._fast_sma(close, 8)  # Slow MA
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            current_fast_ma = float(sma_fast.iloc[-1]) if not pd.isna(sma_fast.iloc[-1]) else current_price
            current_slow_ma = float(sma_slow.iloc[-1]) if not pd.isna(sma_slow.iloc[-1]) else current_price
            
            # RSI Slope calculation
            rsi_slope = 0.0
            if len(rsi) >= 3:  # FIXED: Only need 3 periods
                rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
                rsi_slope = current_rsi - rsi_prev
            
            # Price momentum
            price_change_1m = ((current_price / close.iloc[-2]) - 1) * 100 if len(close) > 1 else 0
            price_change_5m = ((current_price / close.iloc[-5]) - 1) * 100 if len(close) > 5 else 0
            
            # Volume analysis
            volume_avg = volume.rolling(5).mean().iloc[-1] if len(volume) >= 5 else volume.iloc[-1]
            volume_surge = float(volume.iloc[-1]) > float(volume_avg) * 1.05  # FIXED: Lower threshold
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # FIXED BUY SIGNAL - MUCH MORE PERMISSIVE
            if (current_rsi > 35 and  # FIXED: 35 instead of traditional momentum
                current_fast_ma > current_slow_ma and  # FIXED: Simple trend confirmation
                # FIXED: Much more permissive momentum requirements
                (rsi_slope > -2.0 or price_change_1m > -0.5)):  # Either RSI not falling fast OR price not falling fast
                
                action = 'buy'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.5  # FIXED: Higher base confidence
                rsi_momentum = max(0, current_rsi - 35)  # FIXED: Use 35 as threshold
                trend_bonus = min(0.3, max(0, (current_fast_ma - current_slow_ma) / current_price * 100))
                volume_bonus = 0.2 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_momentum / 30) + trend_bonus + volume_bonus)
                reason = f'FIXED Momentum BUY: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), trend={price_change_5m:.2f}%'
                
            # FIXED SELL SIGNAL - MUCH MORE PERMISSIVE
            elif (current_rsi < 65 and  # FIXED: 65 instead of traditional momentum
                  current_fast_ma < current_slow_ma and  # FIXED: Simple trend confirmation
                  # FIXED: Much more permissive momentum requirements
                  (rsi_slope < 2.0 or price_change_1m < 0.5)):  # Either RSI not rising fast OR price not rising fast
                
                action = 'sell'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.5  # FIXED: Higher base confidence
                rsi_momentum = max(0, 65 - current_rsi)  # FIXED: Use 65 as threshold
                trend_bonus = min(0.3, max(0, (current_slow_ma - current_fast_ma) / current_price * 100))
                volume_bonus = 0.2 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_momentum / 30) + trend_bonus + volume_bonus)
                reason = f'FIXED Momentum SELL: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), trend={price_change_5m:.2f}%'

            # Set stop loss and take profit using centralized parameters
            if action == 'buy':
                stop_loss = current_price * (1 - 0.003)  # 0.30% stop loss
                take_profit = current_price * (1 + 0.006)  # 0.60% profit target
            elif action == 'sell':
                stop_loss = current_price * (1 + 0.003)  # 0.30% stop loss
                take_profit = current_price * (1 - 0.006)  # 0.60% profit target
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
                'price_change_1m': price_change_1m,
                'price_change_5m': price_change_5m,
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
    
    def _fast_sma(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period, min_periods=1).mean()
    
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

class EarlyGCPDetector:
    """Early Growth-Plateau Pattern Detector"""
    
    def __init__(self):
        self.name = "GCP-Detector"
    
    def detect_early_gcp_pattern(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Detect early GCP patterns with much more permissive thresholds"""
        try:
            if df.empty or len(df) < 15:  # FIXED: Much lower minimum
                return None
            
            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate basic indicators
            rsi = self._calculate_rsi(close, 7)
            sma_fast = self._fast_sma(close, 3)
            sma_slow = self._fast_sma(close, 8)
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            
            # FIXED: Much more permissive momentum detection
            price_change_1m = ((current_price / close.iloc[-2]) - 1) * 100 if len(close) > 1 else 0
            price_change_5m = ((current_price / close.iloc[-5]) - 1) * 100 if len(close) > 5 else 0
            
            # RSI momentum
            rsi_slope = 0.0
            if len(rsi) >= 3:
                rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
                rsi_slope = current_rsi - rsi_prev
            
            # Volume analysis
            volume_avg = volume.rolling(5).mean().iloc[-1] if len(volume) >= 5 else volume.iloc[-1]
            volume_surge = float(volume.iloc[-1]) > float(volume_avg) * 1.05  # FIXED: Lower threshold
            
            confidence = 0.0
            action = 'hold'
            reason = 'No GCP pattern'
            
            # FIXED: Much more permissive GCP detection
            if (current_rsi > 35 and  # FIXED: Lower threshold
                price_change_5m > 0.5 and  # FIXED: Lower threshold
                (rsi_slope > -1.0 or price_change_1m > -0.3)):  # FIXED: Much more permissive
                
                action = 'buy'
                base_confidence = 0.5
                momentum_bonus = min(0.3, max(0, price_change_5m / 10))
                volume_bonus = 0.2 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + momentum_bonus + volume_bonus)
                reason = f'GCP BUY: RSI={current_rsi:.1f}, momentum={price_change_5m:.2f}%'
                
            elif (current_rsi < 65 and  # FIXED: Lower threshold
                  price_change_5m < -0.5 and  # FIXED: Lower threshold
                  (rsi_slope < 1.0 or price_change_1m < 0.3)):  # FIXED: Much more permissive
                
                action = 'sell'
                base_confidence = 0.5
                momentum_bonus = min(0.3, max(0, abs(price_change_5m) / 10))
                volume_bonus = 0.2 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + momentum_bonus + volume_bonus)
                reason = f'GCP SELL: RSI={current_rsi:.1f}, momentum={price_change_5m:.2f}%'
            
            return {
                'action': action,
                'confidence': confidence,
                'reason': reason
            }
            
        except Exception as e:
            return None
    
    def _fast_sma(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period, min_periods=1).mean()
    
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
