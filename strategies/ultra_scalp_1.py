#!/usr/bin/env python3
"""
ULTRA-SCALP STRATEGY MODULE
Replacement for GitHub repository - FIXED VERSION
Based on working code with permissive parameters
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class UltraScalpStrategy:
    """FIXED Ultra-scalp strategy - MUCH MORE PERMISSIVE"""
    
    def __init__(self):
        self.name = "Ultra-Scalp"
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < 5:  # FIXED: Much lower minimum
                return self._empty_signal('Insufficient data')

            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate indicators using centralized parameters
            rsi = self._calculate_rsi(close, BotConfig.ULTRA_SCALP_RSI_PERIOD)
            sma = self._fast_sma(close, BotConfig.ULTRA_SCALP_SMA_PERIOD)
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            current_sma = float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else current_price
            
            # RSI Slope calculation (momentum confirmation)
            rsi_slope = 0.0
            if len(rsi) >= 3:  # FIXED: Only need 3 periods instead of 4
                rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
                rsi_slope = current_rsi - rsi_prev
            
            # Price Action confirmation
            price_change_1m = ((current_price / close.iloc[-2]) - 1) * 100 if len(close) > 1 else 0
            
            # Volume momentum
            volume_avg = volume.rolling(3).mean().iloc[-1] if len(volume) >= 3 else volume.iloc[-1]
            volume_surge = float(volume.iloc[-1]) > float(volume_avg) * 1.1
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # FIXED BUY SIGNAL - MUCH MORE PERMISSIVE
            if (current_rsi < BotConfig.ULTRA_SCALP_RSI_BUY_THRESHOLD and  # Oversold condition
                # FIXED: Much more permissive momentum requirements
                (rsi_slope > -1.0 or price_change_1m > -0.5)):  # Either RSI not falling fast OR price not falling fast
                
                action = 'buy'
                
                # FIXED: More generous confidence calculation
                base_confidence = BotConfig.ULTRA_SCALP_BASE_CONFIDENCE  # 0.5
                rsi_distance = BotConfig.ULTRA_SCALP_RSI_BUY_THRESHOLD - current_rsi
                momentum_bonus = min(0.2, max(0, rsi_slope / 10 + price_change_1m / 100))
                volume_bonus = 0.1 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / BotConfig.ULTRA_SCALP_RSI_CONFIDENCE_FACTOR) + momentum_bonus + volume_bonus)
                reason = f'FIXED Ultra-scalp BUY: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_change_1m:.2f}%'
                
            # FIXED SELL SIGNAL - MUCH MORE PERMISSIVE
            elif (current_rsi > BotConfig.ULTRA_SCALP_RSI_SELL_THRESHOLD and  # Overbought condition
                  # FIXED: Much more permissive momentum requirements
                  (rsi_slope < 1.0 or price_change_1m < 0.5)):  # Either RSI not rising fast OR price not rising fast
                
                action = 'sell'
                
                # FIXED: More generous confidence calculation
                base_confidence = BotConfig.ULTRA_SCALP_BASE_CONFIDENCE  # 0.5
                rsi_distance = current_rsi - BotConfig.ULTRA_SCALP_RSI_SELL_THRESHOLD
                momentum_bonus = min(0.2, max(0, abs(rsi_slope) / 10 + abs(price_change_1m) / 100))
                volume_bonus = 0.1 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + (rsi_distance / BotConfig.ULTRA_SCALP_RSI_CONFIDENCE_FACTOR) + momentum_bonus + volume_bonus)
                reason = f'FIXED Ultra-scalp SELL: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_change_1m:.2f}%'

            # Set stop loss and take profit using centralized parameters
            if action == 'buy':
                stop_loss = current_price * (1 - BotConfig.ULTRA_SCALP_STOP_LOSS)
                take_profit = current_price * (1 + BotConfig.ULTRA_SCALP_PROFIT_TARGET)
            elif action == 'sell':
                stop_loss = current_price * (1 + BotConfig.ULTRA_SCALP_STOP_LOSS)
                take_profit = current_price * (1 - BotConfig.ULTRA_SCALP_PROFIT_TARGET)
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
                'target_hold': f'{BotConfig.ULTRA_SCALP_MAX_HOLD_SECONDS//60} minutes',
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
            'max_hold_time': 600,
            'target_hold': '10 minutes'
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
