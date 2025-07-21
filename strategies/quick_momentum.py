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
            fast_ma = self._calculate_ema(close, BotConfig.MOMENTUM_FAST_MA_PERIOD)
            slow_ma = self._calculate_ema(close, BotConfig.MOMENTUM_SLOW_MA_PERIOD)
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            current_fast_ma = float(fast_ma.iloc[-1]) if not pd.isna(fast_ma.iloc[-1]) else current_price
            current_slow_ma = float(slow_ma.iloc[-1]) if not pd.isna(slow_ma.iloc[-1]) else current_price
            
            # Moving average crossover
            ma_crossover = current_fast_ma > current_slow_ma
            
            # RSI Slope calculation
            rsi_slope = 0.0
            if len(rsi) >= 3:
                rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
                rsi_slope = current_rsi - rsi_prev
            
            # Price momentum
            price_change_5m = ((current_price / close.iloc[-6]) - 1) * 100 if len(close) > 5 else 0
            
            # Trend confirmation
            trend_periods = min(BotConfig.MOMENTUM_TREND_PERIODS, len(close) - 1)
            price_trend = 0.0
            if trend_periods > 0:
                recent_prices = close.iloc[-trend_periods-1:]
                price_trend = ((recent_prices.iloc[-1] / recent_prices.iloc[0]) - 1) * 100
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # FIXED BUY SIGNAL - MUCH MORE PERMISSIVE
            if (current_rsi < BotConfig.MOMENTUM_RSI_BUY_THRESHOLD and  # Oversold condition
                ma_crossover and  # Fast MA above slow MA
                abs(price_trend) >= BotConfig.MOMENTUM_MIN_PRICE_CHANGE):  # Minimum price change
                
                action = 'buy'
                
                # FIXED: More generous confidence calculation
                base_confidence = BotConfig.MOMENTUM_BASE_CONFIDENCE  # 0.5
                rsi_distance = BotConfig.MOMENTUM_RSI_BUY_THRESHOLD - current_rsi
                trend_bonus = BotConfig.MOMENTUM_TREND_CONFIDENCE_BONUS if price_trend > 0 else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / 30) + trend_bonus)
                reason = f'FIXED Quick-momentum BUY: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_trend:.2f}%'
                
            # FIXED SELL SIGNAL - MUCH MORE PERMISSIVE
            elif (current_rsi > BotConfig.MOMENTUM_RSI_SELL_THRESHOLD and  # Overbought condition
                  not ma_crossover and  # Fast MA below slow MA
                  abs(price_trend) >= BotConfig.MOMENTUM_MIN_PRICE_CHANGE):  # Minimum price change
                
                action = 'sell'
                
                # FIXED: More generous confidence calculation
                base_confidence = BotConfig.MOMENTUM_BASE_CONFIDENCE  # 0.5
                rsi_distance = current_rsi - BotConfig.MOMENTUM_RSI_SELL_THRESHOLD
                trend_bonus = BotConfig.MOMENTUM_TREND_CONFIDENCE_BONUS if price_trend < 0 else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / 30) + trend_bonus)
                reason = f'FIXED Quick-momentum SELL: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_trend:.2f}%'

            # Set stop loss and take profit using centralized parameters
            if action == 'buy':
                stop_loss = current_price * (1 - BotConfig.MOMENTUM_STOP_LOSS)
                take_profit = current_price * (1 + BotConfig.MOMENTUM_PROFIT_TARGET)
            elif action == 'sell':
                stop_loss = current_price * (1 + BotConfig.MOMENTUM_STOP_LOSS)
                take_profit = current_price * (1 - BotConfig.MOMENTUM_PROFIT_TARGET)
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
                'max_hold_time': BotConfig.MOMENTUM_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.MOMENTUM_MAX_HOLD_SECONDS//60} minutes',
                'rsi': current_rsi,
                'rsi_slope': rsi_slope,
                'price_trend': price_trend,
                'ma_crossover': ma_crossover
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
            return pd.Series([50] * len(close), index=close.index), pd.Series([50] * len(close), index=close.index)
    
    def _calculate_macd(self, data: pd.Series, fast: int, slow: int, signal: int):
        """Calculate MACD"""
        try:
            ema_fast = data.ewm(span=fast, adjust=False).mean()
            ema_slow = data.ewm(span=slow, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            histogram = macd_line - signal_line
            
            return macd_line.fillna(0), signal_line.fillna(0), histogram.fillna(0)
        except Exception as e:
            return pd.Series([0] * len(data), index=data.index), pd.Series([0] * len(data), index=data.index), pd.Series([0] * len(data), index=data.index)

# Export the strategy class
__all__ = ['QuickMomentumStrategy']
