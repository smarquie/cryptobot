#!/usr/bin/env python3
"""
ULTRA-SCALP STRATEGY MODULE - CENTRALIZED VERSION
All parameters moved to config.py for centralized management
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from cryptobot.config import BotConfig

class UltraScalpStrategy:
    """Ultra-scalp strategy using centralized parameters from config"""
    
    def __init__(self):
        self.name = "Ultra-Scalp"
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < BotConfig.MIN_DATA_POINTS:
                return self._empty_signal('Insufficient data')

            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate indicators using config parameters
            rsi = self._calculate_rsi(close, BotConfig.ULTRA_SCALP_RSI_PERIOD)
            sma = self._fast_sma(close, BotConfig.ULTRA_SCALP_SMA_PERIOD)
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            current_sma = float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else current_price
            
            # RSI Slope calculation using config parameters
            rsi_slope = 0.0
            if len(rsi) >= 3:
                rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
                rsi_slope = current_rsi - rsi_prev
            
            # Price Action confirmation using config parameters
            price_change_1m = ((current_price / close.iloc[-2]) - 1) * 100 if len(close) > 1 else 0
            
            # Volume momentum using config parameters
            volume_avg = volume.rolling(BotConfig.VOLUME_AVERAGE_PERIOD).mean().iloc[-1] if len(volume) >= BotConfig.VOLUME_AVERAGE_PERIOD else volume.iloc[-1]
            volume_surge = float(volume.iloc[-1]) > float(volume_avg) * BotConfig.VOLUME_SURGE_THRESHOLD
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # BUY SIGNAL using config parameters
            if (current_rsi < BotConfig.ULTRA_SCALP_RSI_OVERSOLD and
                (rsi_slope > BotConfig.ULTRA_SCALP_RSI_SLOPE_THRESHOLD or 
                 price_change_1m > BotConfig.ULTRA_SCALP_PRICE_CHANGE_THRESHOLD)):
                
                action = 'buy'
                
                # Confidence calculation using config parameters
                base_confidence = BotConfig.ULTRA_SCALP_BASE_CONFIDENCE
                rsi_distance = BotConfig.ULTRA_SCALP_RSI_OVERSOLD - current_rsi
                momentum_bonus = min(BotConfig.ULTRA_SCALP_MOMENTUM_BONUS_MAX, 
                                   max(0, rsi_slope / 10 + price_change_1m / 100))
                volume_bonus = BotConfig.ULTRA_SCALP_VOLUME_BONUS if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / BotConfig.ULTRA_SCALP_RSI_DISTANCE_DIVISOR) + momentum_bonus + volume_bonus)
                reason = f'Ultra-scalp BUY: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_change_1m:.2f}%'
                
            # SELL SIGNAL using config parameters
            elif (current_rsi > BotConfig.ULTRA_SCALP_RSI_OVERBOUGHT and
                  (rsi_slope < -BotConfig.ULTRA_SCALP_RSI_SLOPE_THRESHOLD or 
                   price_change_1m < -BotConfig.ULTRA_SCALP_PRICE_CHANGE_THRESHOLD)):
                
                action = 'sell'
                
                # Confidence calculation using config parameters
                base_confidence = BotConfig.ULTRA_SCALP_BASE_CONFIDENCE
                rsi_distance = current_rsi - BotConfig.ULTRA_SCALP_RSI_OVERBOUGHT
                momentum_bonus = min(BotConfig.ULTRA_SCALP_MOMENTUM_BONUS_MAX, 
                                   max(0, abs(rsi_slope) / 10 + abs(price_change_1m) / 100))
                volume_bonus = BotConfig.ULTRA_SCALP_VOLUME_BONUS if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / BotConfig.ULTRA_SCALP_RSI_DISTANCE_DIVISOR) + momentum_bonus + volume_bonus)
                reason = f'Ultra-scalp SELL: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_change_1m:.2f}%'

            # Set stop loss and take profit using config parameters
            if action == 'buy':
                stop_loss = current_price * (1 - BotConfig.ULTRA_SCALP_STOP_LOSS_PERCENT)
                take_profit = current_price * (1 + BotConfig.ULTRA_SCALP_TAKE_PROFIT_PERCENT)
            elif action == 'sell':
                stop_loss = current_price * (1 + BotConfig.ULTRA_SCALP_STOP_LOSS_PERCENT)
                take_profit = current_price * (1 - BotConfig.ULTRA_SCALP_TAKE_PROFIT_PERCENT)
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
                'max_hold_time': BotConfig.ULTRA_SCALP_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.ULTRA_SCALP_MAX_HOLD_SECONDS // 60} minutes',
                'rsi': current_rsi,
                'rsi_slope': rsi_slope,
                'price_change_1m': price_change_1m,
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
            'max_hold_time': BotConfig.ULTRA_SCALP_MAX_HOLD_SECONDS,
            'target_hold': f'{BotConfig.ULTRA_SCALP_MAX_HOLD_SECONDS // 60} minutes'
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
__all__ = ['UltraScalpStrategy']
