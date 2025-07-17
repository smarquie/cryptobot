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
            # Growth phase detection
            if (current_rsi > 35 and  # FIXED: Lower threshold from 50
                rsi_slope > -2.0 and  # FIXED: Much more permissive
                price_change_1m > -0.3 and  # FIXED: Much more permissive
                price_change_5m > -1.0):  # FIXED: Much more permissive
                
                action = 'buy'
                base_confidence = 0.2  # FIXED: Lower base confidence
                rsi_bonus = min(0.2, (current_rsi - 35) / 30)  # FIXED: Use 35 as base
                momentum_bonus = min(0.2, max(0, rsi_slope / 10 + price_change_1m / 100))
                volume_bonus = 0.1 if volume_surge else 0.05  # FIXED: Give bonus even without volume
                
                confidence = min(0.9, base_confidence + rsi_bonus + momentum_bonus + volume_bonus)
                reason = f'GCP Growth BUY: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_change_1m:.2f}%'
                
            # Plateau phase detection
            elif (current_rsi < 65 and  # FIXED: Lower threshold from 70
                  rsi_slope < 2.0 and  # FIXED: Much more permissive
                  price_change_1m < 0.3 and  # FIXED: Much more permissive
                  price_change_5m < 1.0):  # FIXED: Much more permissive
                
                action = 'sell'
                base_confidence = 0.2  # FIXED: Lower base confidence
                rsi_bonus = min(0.2, (65 - current_rsi) / 30)  # FIXED: Use 65 as base
                momentum_bonus = min(0.2, max(0, abs(rsi_slope) / 10 + abs(price_change_1m) / 100))
                volume_bonus = 0.1 if volume_surge else 0.05  # FIXED: Give bonus even without volume
                
                confidence = min(0.9, base_confidence + rsi_bonus + momentum_bonus + volume_bonus)
                reason = f'GCP Plateau SELL: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_change_1m:.2f}%'
            
            if action != 'hold':
                # Set stop loss and take profit
                if action == 'buy':
                    stop_loss = current_price * (1 - 0.003)  # 0.30% stop loss
                    take_profit = current_price * (1 + 0.006)  # 0.60% profit target
                else:
                    stop_loss = current_price * (1 + 0.003)  # 0.30% stop loss
                    take_profit = current_price * (1 - 0.006)  # 0.60% profit target
                
                return {
                    'action': action,
                    'confidence': confidence,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'reason': reason,
                    'max_hold_time': 1800,  # 30 minutes
                    'target_hold': '30 minutes',
                    'pattern_type': 'GCP',
                    'growth_details': {
                        'rsi': current_rsi,
                        'rsi_slope': rsi_slope,
                        'price_change_1m': price_change_1m,
                        'price_change_5m': price_change_5m,
                        'volume_surge': volume_surge
                    }
                }
            
            return None
            
        except Exception as e:
            return None

class CompleteQuickMomentumStrategy:
    """FIXED Quick-Momentum Strategy using Early GCP Pattern Detection"""
    
    def __init__(self):
        self.name = "Quick-Momentum"
        self.gcp_detector = EarlyGCPDetector()
        
        # Keep original parameters for compatibility
        self.MOMENTUM_MIN_CONFIDENCE = 0.2  # FIXED: Much lower
        self.MOMENTUM_MAX_HOLD_SECONDS = 1800
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Analyze market data and generate trading signals using Early GCP detection"""
        try:
            if df.empty or len(df) < 15:  # FIXED: Much lower minimum
                return self._empty_signal('Insufficient data for GCP analysis')

            # Use the Early GCP detector
            gcp_signal = self.gcp_detector.detect_early_gcp_pattern(df, symbol)
            
            if gcp_signal:
                # Convert GCP signal to momentum strategy format
                return {
                    'action': gcp_signal['action'],
                    'confidence': gcp_signal['confidence'],
                    'strategy': self.name,  # Keep original strategy name
                    'entry_price': gcp_signal['entry_price'],
                    'stop_loss': gcp_signal['stop_loss'],
                    'take_profit': gcp_signal['take_profit'],
                    'reason': f'GCP {gcp_signal["reason"]}',
                    'max_hold_time': gcp_signal['max_hold_time'],
                    'target_hold': gcp_signal['target_hold'],
                    'gcp_pattern_type': gcp_signal.get('pattern_type', 'Unknown'),
                    'growth_details': gcp_signal.get('growth_details', {}),
                    'plateau_details': gcp_signal.get('plateau_details', {})
                }
            else:
                return self._empty_signal('No GCP pattern detected')

        except Exception as e:
            return self._empty_signal(f'GCP Analysis Error: {e}')

    def _empty_signal(self, reason: str) -> Dict:
        """Return empty signal with original momentum strategy format"""
        return {
            'action': 'hold',
            'confidence': 0.0,
            'strategy': self.name,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'reason': reason,
            'max_hold_time': self.MOMENTUM_MAX_HOLD_SECONDS,
            'target_hold': f'{self.MOMENTUM_MAX_HOLD_SECONDS//60} minutes'
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

# Export the strategy classes
__all__ = ['CompleteQuickMomentumStrategy', 'EarlyGCPDetector']
