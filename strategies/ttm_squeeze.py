#!/usr/bin/env python3
"""
TTM-SQUEEZE STRATEGY MODULE - FIXED TO MATCH COMPLETE BOT
Complete replication of the TTM strategy from complete_4_strategies_bot.py
All input/output interfaces preserved for compatibility
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from cryptobot.config import BotConfig

class TTMSqueezeStrategy:
    """TTM-Squeeze strategy - EXACT replica of complete bot version"""
    
    def __init__(self):
        self.name = "TTM-Squeeze"
        self.squeeze_history = {}  # Track squeeze periods per symbol - CRITICAL for complete bot logic
        
        # Load parameters from BotConfig
        self.config = {
            # Bollinger Bands
            "bb_period": BotConfig.TTM_BB_PERIOD,
            "bb_std_dev": BotConfig.TTM_BB_STD_DEV,
            
            # Keltner Channels
            "kc_period": BotConfig.TTM_KC_PERIOD,
            "kc_atr_multiplier": BotConfig.TTM_KC_ATR_MULTIPLIER,
            
            # Donchian
            "donchian_period": BotConfig.TTM_DONCHIAN_PERIOD,
            
            # CVD
            "cvd_period": BotConfig.TTM_CVD_PERIOD,
            
            # Entry conditions
            "momentum_threshold": BotConfig.TTM_MOMENTUM_THRESHOLD,
            "squeeze_persistence": BotConfig.TTM_SQUEEZE_PERSISTENCE,
            
            # Risk management
            "stop_loss_percent": BotConfig.TTM_STOP_LOSS_PERCENT,
            "take_profit_percent": BotConfig.TTM_TAKE_PROFIT_PERCENT,

            "adx_threshold": BotConfig.TTM_ADX_THRESHOLD,
            "bb_width_percentile": BotConfig.TTM_BB_WIDTH_PERCENTILE,
        }
    
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            # Use config period for data check
            min_periods = max(
                self.config["bb_period"],
                self.config["kc_period"],
                self.config["donchian_period"],
                self.config["cvd_period"]
            )
            
            if len(df) < min_periods:
                return self._empty_signal(f'Need {min_periods}+ candles, got {len(df)}')

            high = df['high']
            low = df['low']
            close = df['close']
            volume = df['volume']
            
            # Calculate indicators with config periods
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close)
            kc_upper, kc_middle, kc_lower = self._calculate_keltner_channels(high, low, close)
            donchian_midline = self._calculate_donchian_midline(high, low)
            cvd = self._calculate_cvd(volume, close)
            # Add ADX calculation
            adx = self._calculate_adx(high, low, close, 14)
            current_adx = adx.iloc[-1]
                    
            # Current values
            current_price = float(close.iloc[-1])
            current_bb_upper = float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else current_price * 1.02
            current_bb_lower = float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else current_price * 0.98
            current_kc_upper = float(kc_upper.iloc[-1]) if not pd.isna(kc_upper.iloc[-1]) else current_price * 1.02
            current_kc_lower = float(kc_lower.iloc[-1]) if not pd.isna(kc_lower.iloc[-1]) else current_price * 0.98
            current_donchian = float(donchian_midline.iloc[-1]) if not pd.isna(donchian_midline.iloc[-1]) else current_price
            current_sma = float(bb_middle.iloc[-1]) if not pd.isna(bb_middle.iloc[-1]) else current_price
            current_cvd = float(cvd.iloc[-1]) if not pd.isna(cvd.iloc[-1]) else 0

            # Current values - add ADX after other indicators
            adx = self._calculate_adx(high, low, close, 14)
            current_adx = float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 25

            # Add this after calculating Bollinger Bands
            bb_width = (bb_upper - bb_lower) / bb_middle
            bb_width_percentile = bb_width.rank(pct=True).iloc[-1] * 100

            # Check squeeze condition (EXACT same logic as complete bot)
            squeeze_on = (current_bb_upper < current_kc_upper and current_bb_lower > current_kc_lower)
            
            # Track squeeze history (CRITICAL - missing from original)
            if symbol not in self.squeeze_history:
                self.squeeze_history[symbol] = []
            
            self.squeeze_history[symbol].append(squeeze_on)
            # Keep only recent history
            if len(self.squeeze_history[symbol]) > 10:
                self.squeeze_history[symbol] = self.squeeze_history[symbol][-10:]
            
            # Calculate momentum (COMPLETE BOT METHOD - totally different from original)
            momentum_delta = current_price - ((current_donchian + current_sma) / 2)
            momentum_normalized = momentum_delta / current_price
            
            # Calculate CVD momentum (COMPLETE BOT FEATURE - missing from original)
            cvd_momentum = 0
            if len(cvd) > 10:
                cvd_change = current_cvd - float(cvd.iloc[-10])
                cvd_momentum = cvd_change / abs(float(cvd.iloc[-10])) if cvd.iloc[-10] != 0 else 0
            
            # Count consecutive squeeze periods (COMPLETE BOT LOGIC - missing from original)
            recent_squeeze_count = 0
            for i in range(len(self.squeeze_history[symbol]) - 1, -1, -1):
                if self.squeeze_history[symbol][i]:
                    recent_squeeze_count += 1
                else:
                    break
            
            confidence = 0.0
            action = 'hold'
            reason = 'No TTM signal'
            
            # COMPLETE BOT ENTRY LOGIC 
            if (self._check_squeeze_persistence(symbol, self.config["squeeze_persistence"]) and
                abs(momentum_normalized) > self.config["momentum_threshold"] and
                current_adx > BotConfig.TTM_ADX_THRESHOLD and  # New ADX filter
                bb_width_percentile < BotConfig.TTM_BB_WIDTH_PERCENTILE):  # New BB width filter

                # Determine direction based on momentum
                if momentum_normalized > 0:
                    action = 'buy'
                    reason = f'TTM BUY: Squeeze + ADX={current_adx:.1f} + momentum={momentum_normalized:.3f}'
                elif momentum_normalized < 0:
                    action = 'sell'
                    reason = f'TTM SELL: Squeeze + ADX={current_adx:.1f} + momentum={momentum_normalized:.3f}'

                
                if action != 'hold':
                    # Calculate confidence (COMPLETE BOT METHOD)
                    confidence = 0.6  # Complete bot base confidence
                    
                    # Bonus for strong squeeze history (COMPLETE BOT LOGIC)
                    if recent_squeeze_count >= 3:
                        confidence += 0.2  # Complete bot squeeze bonus
                    
                    # Bonus for strong momentum (COMPLETE BOT LOGIC)
                    if abs(momentum_normalized) > 0.3 * 1.5:  # 1.5x threshold
                        confidence += 0.1
                    
                    confidence = min(0.95, confidence)

            # Set stop loss and take profit (COMPLETE BOT VALUES - different from original)
            if action == 'buy':
                stop_loss = current_price * (1 - self.config["stop_loss_percent"])
                take_profit = current_price * (1 + self.config["take_profit_percent"])
            elif action == 'sell':
                stop_loss = current_price * (1 + self.config["stop_loss_percent"])
                take_profit = current_price * (1 - self.config["take_profit_percent"])
            else:
                stop_loss = current_price
                take_profit = current_price

            # Return in EXACT same format as original (interface preserved)
            return {
                'action': action,
                'confidence': confidence,
                'strategy': self.name,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'reason': reason,
                'max_hold_time': BotConfig.TTM_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.TTM_MAX_HOLD_SECONDS//60} minutes',
                # Additional complete bot data (keeping original interface plus new data)
                'squeeze_on': squeeze_on,
                'squeeze_count': recent_squeeze_count,
                'momentum': momentum_normalized,
                'cvd_momentum': cvd_momentum,
                # Keep original interface elements that might be expected
                'bb_position': (current_price - current_bb_lower) / (current_bb_upper - current_bb_lower) if (current_bb_upper - current_bb_lower) > 0 else 0.5,
                'keltner_position': (current_price - current_kc_lower) / (current_kc_upper - current_kc_lower) if (current_kc_upper - current_kc_lower) > 0 else 0.5,
                'volume_surge': False,  # Original had this, keeping for compatibility
                'adx': current_adx,
                'bb_width_percentile': bb_width_percentile,
            }

        except Exception as e:
            return self._empty_signal(f'TTM Error: {e}')

    def _check_squeeze_persistence(self, symbol: str, required_periods: int) -> bool:
        """Check if squeeze has persisted for N consecutive periods"""
        if symbol not in self.squeeze_history or len(self.squeeze_history[symbol]) < required_periods:
            return False
        
        # Check last N periods
        return all(self.squeeze_history[symbol][-i] for i in range(1, required_periods+1))
    
    def _empty_signal(self, reason: str) -> Dict:
        """Same interface as original"""
        return {
            'action': 'hold',
            'confidence': 0.0,
            'strategy': self.name,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'reason': reason,
            'max_hold_time': BotConfig.TTM_MAX_HOLD_SECONDS,
            'target_hold': f'{BotConfig.TTM_MAX_HOLD_SECONDS//60} minutes'
        }
    
    def _calculate_rsi(self, data: pd.Series, period: int) -> pd.Series:
        """Keep original RSI method for compatibility (even though not used in complete bot logic)"""
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
    
    def _calculate_bollinger_bands(self, data: pd.Series, period: int = None, std_dev: float = None):
        """UPDATED - Complete bot method with min_periods handling"""
        try:
            period = period or self.config["bb_period"]
            std_dev = std_dev or self.config["bb_std_dev"]
            
            sma = data.rolling(window=period, min_periods=1).mean()
            std = data.rolling(window=period, min_periods=1).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return upper_band.fillna(data), sma.fillna(data), lower_band.fillna(data)
        except Exception as e:
            return data * 1.02, data, data * 0.98
    
    def _calculate_keltner_channels(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = None, atr_multiplier: float = None):
        """UPDATED - Complete bot method using close SMA (not typical price)"""
        try:
            period = period or self.config["kc_period"]
            atr_multiplier = atr_multiplier or self.config["kc_atr_multiplier"]
            
            # Complete bot uses close SMA, not typical price
            sma = close.rolling(window=period, min_periods=1).mean()
            atr = self._calculate_atr(high, low, close, period)
            
            upper_channel = sma + (atr * atr_multiplier)
            lower_channel = sma - (atr * atr_multiplier)
            
            return upper_channel.fillna(close), sma.fillna(close), lower_channel.fillna(close)
        except Exception as e:
            return close * 1.02, close, close * 0.98
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = None) -> pd.Series:
        """UPDATED - Complete bot method with min_periods handling"""
        try:
            period = period or self.config["kc_period"]  # Use same period as Keltner
            
            prev_close = close.shift(1)
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period, min_periods=1).mean()
            
            return atr.fillna(0)
        except Exception as e:
            return pd.Series([0] * len(high), index=high.index)

    def _calculate_donchian_midline(self, high: pd.Series, low: pd.Series, period: int = None) -> pd.Series:
        """NEW METHOD - Complete bot feature missing from original"""
        try:
            period = period or self.config["donchian_period"]
            
            highest_high = high.rolling(window=period, min_periods=1).max()
            lowest_low = low.rolling(window=period, min_periods=1).min()
            
            midline = (highest_high + lowest_low) / 2
            return midline.fillna(0)
        except Exception as e:
            return pd.Series([0] * len(high), index=high.index)
    
    def _calculate_cvd(self, volume: pd.Series, close: pd.Series, period: int = None) -> pd.Series:
        """NEW METHOD - Complete bot feature missing from original"""
        try:
            # Simplified CVD: positive volume on up moves, negative on down moves
            price_change = close.diff()
            volume_delta = volume * np.sign(price_change)
            
            # Cumulative sum
            cvd = volume_delta.cumsum()
            return cvd.fillna(0)
        except Exception as e:
            return pd.Series([0] * len(volume), index=volume.index)

    def _calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
        """Calculate ADX for trend strength confirmation"""
        try:
            # Calculate +DI and -DI
            up = high.diff()
            down = -low.diff()
            plus_dm = up.where((up > down) & (up > 0), 0)
            minus_dm = down.where((down > up) & (down > 0), 0)
            
            tr1 = high - low
            tr2 = (high - close.shift()).abs()
            tr3 = (low - close.shift()).abs()
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            atr = true_range.rolling(period).mean()
            plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
            
            dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di))
            adx = dx.rolling(period).mean()
            
            return adx.fillna(25)  # Default to neutral value if not enough data
        except Exception as e:
            return pd.Series([25] * len(high), index=high.index

# Export the strategy class (same as original)
__all__ = ['TTMSqueezeStrategy']
