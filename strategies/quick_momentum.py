#!/usr/bin/env python3
"""
QUICK-MOMENTUM STRATEGY MODULE - CENTRALIZED VERSION
All parameters moved to config.py for centralized management
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from config import BotConfig

class QuickMomentumStrategy:
    """Quick-momentum strategy using centralized parameters from config"""
    
    def __init__(self):
        self.name = "Quick-Momentum"
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < BotConfig.MIN_DATA_POINTS:
                return self._empty_signal('Insufficient data')

            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate indicators using config parameters
            rsi = self._calculate_rsi(close, BotConfig.QUICK_MOMENTUM_RSI_PERIOD)
            fast_ma = self._fast_sma(close, BotConfig.QUICK_MOMENTUM_FAST_MA_PERIOD)
            slow_ma = self._fast_sma(close, BotConfig.QUICK_MOMENTUM_SLOW_MA_PERIOD)
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            current_fast_ma = float(fast_ma.iloc[-1]) if not pd.isna(fast_ma.iloc[-1]) else current_price
            current_slow_ma = float(slow_ma.iloc[-1]) if not pd.isna(slow_ma.iloc[-1]) else current_price
            
            # Momentum calculation using config parameters
            price_change_1m = ((current_price / close.iloc[-2]) - 1) * 100 if len(close) > 1 else 0
            price_change_3m = ((current_price / close.iloc[-4]) - 1) * 100 if len(close) > 3 else 0
            
            # Trend confirmation using config parameters
            ma_trend = current_fast_ma > current_slow_ma
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # BUY SIGNAL using config parameters
            if (current_rsi < BotConfig.QUICK_MOMENTUM_RSI_BUY_THRESHOLD and
                ma_trend and  # Fast MA above slow MA
                price_change_1m > BotConfig.QUICK_MOMENTUM_MOMENTUM_THRESHOLD):
                
                action = 'buy'
                
                # Confidence calculation using config parameters
                base_confidence = BotConfig.QUICK_MOMENTUM_BASE_CONFIDENCE
                rsi_bonus = max(0, (BotConfig.QUICK_MOMENTUM_RSI_BUY_THRESHOLD - current_rsi) / BotConfig.QUICK_MOMENTUM_RSI_DISTANCE_DIVISOR)
                momentum_bonus = min(BotConfig.QUICK_MOMENTUM_MOMENTUM_BONUS_MAX, max(0, price_change_1m / 100))
                
                confidence = min(0.9, base_confidence + rsi_bonus + momentum_bonus)
                reason = f'Quick-momentum BUY: RSI={current_rsi:.1f}, MA trend={ma_trend}, momentum={price_change_1m:.2f}%'
                
            # SELL SIGNAL using config parameters
            elif (current_rsi > BotConfig.QUICK_MOMENTUM_RSI_SELL_THRESHOLD and
                  not ma_trend and  # Fast MA below slow MA
                  price_change_1m < -BotConfig.QUICK_MOMENTUM_MOMENTUM_THRESHOLD):
                
                action = 'sell'
                
                # Confidence calculation using config parameters
                base_confidence = BotConfig.QUICK_MOMENTUM_BASE_CONFIDENCE
                rsi_bonus = max(0, (current_rsi - BotConfig.QUICK_MOMENTUM_RSI_SELL_THRESHOLD) / BotConfig.QUICK_MOMENTUM_RSI_DISTANCE_DIVISOR)
                momentum_bonus = min(BotConfig.QUICK_MOMENTUM_MOMENTUM_BONUS_MAX, max(0, abs(price_change_1m) / 100))
                
                confidence = min(0.9, base_confidence + rsi_bonus + momentum_bonus)
                reason = f'Quick-momentum SELL: RSI={current_rsi:.1f}, MA trend={ma_trend}, momentum={price_change_1m:.2f}%'

            # Set stop loss and take profit using config parameters
            if action == 'buy':
                stop_loss = current_price * (1 - BotConfig.QUICK_MOMENTUM_STOP_LOSS_PERCENT)
                take_profit = current_price * (1 + BotConfig.QUICK_MOMENTUM_TAKE_PROFIT_PERCENT)
            elif action == 'sell':
                stop_loss = current_price * (1 + BotConfig.QUICK_MOMENTUM_STOP_LOSS_PERCENT)
                take_profit = current_price * (1 - BotConfig.QUICK_MOMENTUM_TAKE_PROFIT_PERCENT)
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
                'max_hold_time': BotConfig.QUICK_MOMENTUM_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.QUICK_MOMENTUM_MAX_HOLD_SECONDS // 60} minutes',
                'rsi': current_rsi,
                'fast_ma': current_fast_ma,
                'slow_ma': current_slow_ma,
                'ma_trend': ma_trend,
                'price_change_1m': price_change_1m,
                'price_change_3m': price_change_3m
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
            'max_hold_time': BotConfig.QUICK_MOMENTUM_MAX_HOLD_SECONDS,
            'target_hold': f'{BotConfig.QUICK_MOMENTUM_MAX_HOLD_SECONDS // 60} minutes'
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

# Export the strategy class
__all__ = ['QuickMomentumStrategy']
