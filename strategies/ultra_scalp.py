#!/usr/bin/env python3
"""
ULTRA-SCALP STRATEGY MODULE
Replacement for GitHub repository - IMPROVED VERSION
Based on working code with your specific improvements:
1. SMA trend confirmation (buy above SMA, sell below SMA)
2. RSI percentage-based slope calculation
3. RSI slope thresholds from config (not hardcoded)
4. Volume condition requirement
5. Removed price change condition
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class UltraScalpStrategy:
    """IMPROVED Ultra-scalp strategy with SMA, percentage RSI slope, and volume conditions"""
    
    def __init__(self):
        self.name = "Ultra-Scalp"
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < 5:  # Keep existing minimum
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
            
            # RSI Slope calculation (IMPROVED: percentage-based)
            rsi_slope_pct = 0.0
            if len(rsi) >= 3:
                rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
                if rsi_prev != 0:  # Avoid division by zero
                    rsi_slope_pct = ((current_rsi - rsi_prev) / rsi_prev) * 100
            
            # Volume condition (NEW: check for higher volume)
            volume_avg = volume.rolling(3).mean().iloc[-1] if len(volume) >= 3 else volume.iloc[-1]
            volume_surge = float(volume.iloc[-1]) > float(volume_avg) * BotConfig.VOLUME_SURGE_THRESHOLD
            high_volume_condition = volume_surge  # Only trade in higher volume conditions
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # IMPROVED BUY SIGNAL
            if (current_rsi < BotConfig.ULTRA_SCALP_RSI_BUY_THRESHOLD and         # RSI oversold
                rsi_slope_pct > BotConfig.RSI_SLOPE_MIN and                      # RSI recovering (from config)
                current_price > current_sma and                                  # Price above SMA (uptrend)
                high_volume_condition):                                          # Higher volume condition
                
                action = 'buy'
                
                # Confidence calculation (keeping existing structure)
                base_confidence = BotConfig.ULTRA_SCALP_BASE_CONFIDENCE
                rsi_distance = BotConfig.ULTRA_SCALP_RSI_BUY_THRESHOLD - current_rsi
                
                # IMPROVED: RSI slope bonus based on percentage
                rsi_slope_bonus = min(0.2, max(0, rsi_slope_pct / 20))  # Scale percentage slope
                volume_bonus = 0.1 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + 
                               (rsi_distance / BotConfig.ULTRA_SCALP_RSI_CONFIDENCE_FACTOR) + 
                               rsi_slope_bonus + volume_bonus)
                
                reason = f'IMPROVED Ultra-scalp BUY: RSI={current_rsi:.1f}(slope:{rsi_slope_pct:.1f}%), above SMA, high volume'
                
            # IMPROVED SELL SIGNAL
            elif (current_rsi > BotConfig.ULTRA_SCALP_RSI_SELL_THRESHOLD and     # RSI overbought
                  rsi_slope_pct < BotConfig.RSI_SLOPE_MAX and                    # RSI declining (from config)
                  current_price < current_sma and                                # Price below SMA (downtrend)
                  high_volume_condition):                                        # Higher volume condition
                
                action = 'sell'
                
                # Confidence calculation (keeping existing structure)
                base_confidence = BotConfig.ULTRA_SCALP_BASE_CONFIDENCE
                rsi_distance = current_rsi - BotConfig.ULTRA_SCALP_RSI_SELL_THRESHOLD
                
                # IMPROVED: RSI slope bonus based on percentage
                rsi_slope_bonus = min(0.2, max(0, abs(rsi_slope_pct) / 20))  # Scale percentage slope
                volume_bonus = 0.1 if volume_surge else 0.0
                
                confidence = min(0.9, base_confidence + 
                               (rsi_distance / BotConfig.ULTRA_SCALP_RSI_CONFIDENCE_FACTOR) + 
                               rsi_slope_bonus + volume_bonus)
                
                reason = f'IMPROVED Ultra-scalp SELL: RSI={current_rsi:.1f}(slope:{rsi_slope_pct:.1f}%), below SMA, high volume'

            # Set stop loss and take profit using centralized parameters (unchanged)
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
                'rsi_slope_pct': rsi_slope_pct,  # Changed from rsi_slope to rsi_slope_pct
                'current_sma': current_sma,      # Added SMA info
                'price_vs_sma': 'above' if current_price > current_sma else 'below',  # Added trend info
                'volume_surge': volume_surge,
                'high_volume_condition': high_volume_condition  # Added volume condition info
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
        """Calculate Simple Moving Average (unchanged)"""
        return data.rolling(window=period, min_periods=1).mean()
    
    def _calculate_rsi(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate RSI (unchanged)"""
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
