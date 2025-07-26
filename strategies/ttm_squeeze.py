#!/usr/bin/env python3
"""
TTM-SQUEEZE STRATEGY MODULE - CENTRALIZED VERSION
All parameters moved to config.py for centralized management
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from config_centralized import BotConfig

class TTMSqueezeStrategy:
    """TTM-Squeeze strategy using centralized parameters from config"""
    
    def __init__(self):
        self.name = "TTM-Squeeze"
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < BotConfig.MIN_DATA_POINTS:
                return self._empty_signal('Insufficient data')

            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate TTM Squeeze indicators using config parameters
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(
                close, 
                BotConfig.TTM_SQUEEZE_BB_PERIOD, 
                BotConfig.TTM_SQUEEZE_BB_STD_DEV
            )
            kc_upper, kc_middle, kc_lower = self._calculate_keltner_channels(
                high, 
                low, 
                close, 
                BotConfig.TTM_SQUEEZE_KC_PERIOD, 
                BotConfig.TTM_SQUEEZE_KC_ATR_MULTIPLIER
            )
            
            # Calculate momentum using config parameters
            momentum = self._calculate_momentum(close, BotConfig.TTM_SQUEEZE_MOMENTUM_PERIOD)
            
            # Calculate CVD (Cumulative Volume Delta)
            cvd = self._calculate_cvd(volume, close)
            
            current_price = float(close.iloc[-1])
            current_bb_upper = float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else current_price
            current_bb_lower = float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else current_price
            current_kc_upper = float(kc_upper.iloc[-1]) if not pd.isna(kc_upper.iloc[-1]) else current_price
            current_kc_lower = float(kc_lower.iloc[-1]) if not pd.isna(kc_lower.iloc[-1]) else current_price
            current_momentum = float(momentum.iloc[-1]) if not pd.isna(momentum.iloc[-1]) else 0.0
            current_cvd = float(cvd.iloc[-1]) if not pd.isna(cvd.iloc[-1]) else 0.0
            
            # Check for squeeze condition using config parameters
            squeeze = (current_bb_upper <= current_kc_upper and current_bb_lower >= current_kc_lower)
            
            # Check for momentum breakout using config parameters
            momentum_breakout = abs(current_momentum) > BotConfig.TTM_SQUEEZE_MOMENTUM_THRESHOLD
            
            # Check for CVD momentum using config parameters
            cvd_momentum = abs(current_cvd) > BotConfig.TTM_SQUEEZE_CVD_THRESHOLD
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # BUY SIGNAL using config parameters
            if (squeeze and  # In squeeze
                momentum_breakout and  # Momentum breakout
                current_momentum > 0 and  # Positive momentum
                current_cvd > 0):  # Positive CVD
                
                action = 'buy'
                
                # Confidence calculation using config parameters
                base_confidence = BotConfig.TTM_SQUEEZE_BASE_CONFIDENCE
                squeeze_bonus = BotConfig.TTM_SQUEEZE_SQUEEZE_BONUS if squeeze else 0.0
                momentum_bonus = min(BotConfig.TTM_SQUEEZE_MOMENTUM_BONUS_MAX, max(0, current_momentum / 10))
                cvd_bonus = min(BotConfig.TTM_SQUEEZE_CVD_BONUS_MAX, max(0, current_cvd / 100))
                
                confidence = min(0.9, base_confidence + squeeze_bonus + momentum_bonus + cvd_bonus)
                reason = f'TTM Squeeze BUY: Squeeze={squeeze}, Momentum={current_momentum:.3f}, CVD={current_cvd:.1f}'
                
            # SELL SIGNAL using config parameters
            elif (squeeze and  # In squeeze
                  momentum_breakout and  # Momentum breakout
                  current_momentum < 0 and  # Negative momentum
                  current_cvd < 0):  # Negative CVD
                
                action = 'sell'
                
                # Confidence calculation using config parameters
                base_confidence = BotConfig.TTM_SQUEEZE_BASE_CONFIDENCE
                squeeze_bonus = BotConfig.TTM_SQUEEZE_SQUEEZE_BONUS if squeeze else 0.0
                momentum_bonus = min(BotConfig.TTM_SQUEEZE_MOMENTUM_BONUS_MAX, max(0, abs(current_momentum) / 10))
                cvd_bonus = min(BotConfig.TTM_SQUEEZE_CVD_BONUS_MAX, max(0, abs(current_cvd) / 100))
                
                confidence = min(0.9, base_confidence + squeeze_bonus + momentum_bonus + cvd_bonus)
                reason = f'TTM Squeeze SELL: Squeeze={squeeze}, Momentum={current_momentum:.3f}, CVD={current_cvd:.1f}'

            # Set stop loss and take profit using config parameters
            if action == 'buy':
                stop_loss = current_price * (1 - BotConfig.TTM_SQUEEZE_STOP_LOSS_PERCENT)
                take_profit = current_price * (1 + BotConfig.TTM_SQUEEZE_TAKE_PROFIT_PERCENT)
            elif action == 'sell':
                stop_loss = current_price * (1 + BotConfig.TTM_SQUEEZE_STOP_LOSS_PERCENT)
                take_profit = current_price * (1 - BotConfig.TTM_SQUEEZE_TAKE_PROFIT_PERCENT)
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
                'max_hold_time': BotConfig.TTM_SQUEEZE_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.TTM_SQUEEZE_MAX_HOLD_SECONDS // 60} minutes',
                'squeeze': squeeze,
                'momentum': current_momentum,
                'cvd': current_cvd,
                'bb_upper': current_bb_upper,
                'bb_lower': current_bb_lower,
                'kc_upper': current_kc_upper,
                'kc_lower': current_kc_lower
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
            'max_hold_time': BotConfig.TTM_SQUEEZE_MAX_HOLD_SECONDS,
            'target_hold': f'{BotConfig.TTM_SQUEEZE_MAX_HOLD_SECONDS // 60} minutes'
        }
    
    def _calculate_bollinger_bands(self, data: pd.Series, period: int, std_dev: float) -> tuple:
        """Calculate Bollinger Bands"""
        try:
            sma = data.rolling(window=period, min_periods=1).mean()
            std = data.rolling(window=period, min_periods=1).std()
            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)
            return upper, sma, lower
        except Exception as e:
            return data, data, data
    
    def _calculate_keltner_channels(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                                   period: int, atr_multiplier: float) -> tuple:
        """Calculate Keltner Channels"""
        try:
            tr = pd.DataFrame({
                'hl': high - low,
                'hc': abs(high - close.shift(1)),
                'lc': abs(low - close.shift(1))
            }).max(axis=1)
            
            atr = tr.rolling(window=period, min_periods=1).mean()
            sma = close.rolling(window=period, min_periods=1).mean()
            
            upper = sma + (atr * atr_multiplier)
            lower = sma - (atr * atr_multiplier)
            
            return upper, sma, lower
        except Exception as e:
            return close, close, close
    
    def _calculate_momentum(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate momentum"""
        try:
            return data - data.shift(period)
        except Exception as e:
            return pd.Series([0] * len(data), index=data.index)
    
    def _calculate_cvd(self, volume: pd.Series, close: pd.Series) -> pd.Series:
        """Calculate Cumulative Volume Delta"""
        try:
            price_change = close.diff()
            volume_delta = volume * np.where(price_change > 0, 1, np.where(price_change < 0, -1, 0))
            return volume_delta.cumsum()
        except Exception as e:
            return pd.Series([0] * len(volume), index=volume.index)

# Export the strategy class
__all__ = ['TTMSqueezeStrategy']
