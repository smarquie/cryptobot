#!/usr/bin/env python3
"""
FAST-SCALP STRATEGY MODULE - REVISED VERSION
More differentiated from Ultra-Scalp with longer RSI period and stricter conditions
Based on working code with careful modifications to maintain functionality
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class FastScalpStrategy:
    """REVISED Fast-scalp strategy - Longer term and more selective"""
    
    def __init__(self):
        self.name = "Fast-Scalp"
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < 15:  # Increased minimum data requirement for 14-period RSI
                return self._empty_signal('Insufficient data')

            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate indicators using longer periods for differentiation
            rsi = self._calculate_rsi(close, 14)  # Changed from 9 to 14 periods
            # Adjusted MACD for longer timeframe analysis
            macd_line, signal_line, histogram = self._calculate_macd(close, 
                                                                   BotConfig.FAST_SCALP_MACD_FAST * 2,  # 10 instead of 5
                                                                   BotConfig.FAST_SCALP_MACD_SLOW * 2,  # 20 instead of 10
                                                                   BotConfig.FAST_SCALP_MACD_SIGNAL * 2)  # 8 instead of 4
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            current_macd = float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else 0.0
            current_signal = float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else 0.0
            
            # MACD crossover
            macd_crossover = current_macd > current_signal
            
            # RSI Slope calculation - using config parameter instead of hardcoded values
            rsi_slope = 0.0
            if len(rsi) >= 3:
                rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
                rsi_slope = current_rsi - rsi_prev
            
            # Price momentum over longer period for this strategy
            price_change_2m = ((current_price / close.iloc[-3]) - 1) * 100 if len(close) > 2 else 0
            
            # Volume analysis - STRICTER requirement for volume increase
            volume_avg = volume.rolling(BotConfig.FAST_SCALP_VOLUME_PERIOD).mean().iloc[-1] if len(volume) >= BotConfig.FAST_SCALP_VOLUME_PERIOD else volume.iloc[-1]
            volume_surge = float(volume.iloc[-1]) > float(volume_avg) * BotConfig.FAST_SCALP_VOLUME_MULTIPLIER
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # REVISED BUY SIGNAL - More selective with volume requirement
            if (current_rsi < BotConfig.FAST_SCALP_RSI_BUY_THRESHOLD and  # Oversold condition
                macd_crossover and  # STRICTER: MACD crossover is now REQUIRED
                volume_surge and  # NEW: Volume surge is now REQUIRED
                rsi_slope > BotConfig.RSI_SLOPE_MIN and  # Using config parameter instead of hardcoded -2.0
                price_change_2m > BotConfig.PRICE_CHANGE_MIN):  # Using config parameter instead of hardcoded -1.0
                
                action = 'buy'
                
                # Enhanced confidence calculation for longer-term signals
                base_confidence = BotConfig.FAST_SCALP_BASE_CONFIDENCE
                rsi_distance = BotConfig.FAST_SCALP_RSI_BUY_THRESHOLD - current_rsi
                
                # Momentum bonus considers both RSI slope and price momentum
                momentum_bonus = min(0.3, max(0, (rsi_slope - BotConfig.RSI_SLOPE_MIN) / 10 + 
                                             (price_change_2m - BotConfig.PRICE_CHANGE_MIN) / 30))
                
                # Volume bonus for meeting the required surge
                volume_bonus = BotConfig.FAST_SCALP_VOLUME_CONFIDENCE_BONUS
                
                # MACD strength bonus (how strong the crossover is)
                macd_strength = min(0.1, max(0, (current_macd - current_signal) / abs(current_signal) * 0.1)) if current_signal != 0 else 0
                
                confidence = min(0.9, base_confidence + (rsi_distance / 25) + momentum_bonus + volume_bonus + macd_strength)
                reason = f'REVISED Fast-scalp BUY: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), MACD crossover, volume surge, momentum={price_change_2m:.2f}%'
                
            # REVISED SELL SIGNAL - More selective with volume requirement
            elif (current_rsi > BotConfig.FAST_SCALP_RSI_SELL_THRESHOLD and  # Overbought condition
                  not macd_crossover and  # STRICTER: No MACD crossover required
                  volume_surge and  # NEW: Volume surge is now REQUIRED
                  rsi_slope < -BotConfig.RSI_SLOPE_MIN and  # Using config parameter, negative for sell (symmetric)
                  price_change_2m < -BotConfig.PRICE_CHANGE_MIN):  # Using config parameter, negative for sell (symmetric)
                
                action = 'sell'
                
                # Enhanced confidence calculation for longer-term signals
                base_confidence = BotConfig.FAST_SCALP_BASE_CONFIDENCE
                rsi_distance = current_rsi - BotConfig.FAST_SCALP_RSI_SELL_THRESHOLD
                
                # Momentum bonus considers both RSI slope and price momentum (symmetric to buy)
                momentum_bonus = min(0.3, max(0, (-rsi_slope - BotConfig.RSI_SLOPE_MIN) / 10 + 
                                             (-price_change_2m - BotConfig.PRICE_CHANGE_MIN) / 30))
                
                # Volume bonus for meeting the required surge
                volume_bonus = BotConfig.FAST_SCALP_VOLUME_CONFIDENCE_BONUS
                
                # MACD strength bonus (how strong the bearish signal is)
                macd_strength = min(0.1, max(0, (current_signal - current_macd) / abs(current_signal) * 0.1)) if current_signal != 0 else 0
                
                confidence = min(0.9, base_confidence + (rsi_distance / 25) + momentum_bonus + volume_bonus + macd_strength)
                reason = f'REVISED Fast-scalp SELL: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), No MACD crossover, volume surge, momentum={price_change_2m:.2f}%'

            # Set stop loss and take profit using centralized parameters
            if action == 'buy':
                stop_loss = current_price * (1 - BotConfig.FAST_SCALP_STOP_LOSS)
                take_profit = current_price * (1 + BotConfig.FAST_SCALP_PROFIT_TARGET)
            elif action == 'sell':
                stop_loss = current_price * (1 + BotConfig.FAST_SCALP_STOP_LOSS)
                take_profit = current_price * (1 - BotConfig.FAST_SCALP_PROFIT_TARGET)
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
                'max_hold_time': BotConfig.FAST_SCALP_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.FAST_SCALP_MAX_HOLD_SECONDS//60} minutes',
                'rsi': current_rsi,
                'rsi_slope': rsi_slope,
                'price_change_2m': price_change_2m,
                'volume_surge': volume_surge,
                'macd_crossover': macd_crossover,
                'macd_strength': abs(current_macd - current_signal) if 'macd_strength' in locals() else 0
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
            'max_hold_time': 900,
            'target_hold': '15 minutes'
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
    
    def _calculate_macd(self, data: pd.Series, fast_period: int, slow_period: int, signal_period: int) -> tuple:
        """Calculate MACD with configurable periods"""
        try:
            ema_fast = self._calculate_ema(data, fast_period)
            ema_slow = self._calculate_ema(data, slow_period)
            
            macd_line = ema_fast - ema_slow
            signal_line = self._calculate_ema(macd_line, signal_period)
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
        except Exception as e:
            # Return neutral values on error
            neutral_series = pd.Series([0] * len(data), index=data.index)
            return neutral_series, neutral_series, neutral_series

# Export the strategy class
__all__ = ['FastScalpStrategy']
