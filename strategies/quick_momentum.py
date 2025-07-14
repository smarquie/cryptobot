# strategies/quick_momentum.py

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base import Strategy
from config import BotConfig
from utils.ta import TechnicalAnalysis

class QuickMomentumStrategy(Strategy):
    def __init__(self):
        super().__init__("Quick-Momentum")
        self.config = BotConfig.MOMENTUM_GCP_CONFIG.get('BTC', {'growth_window': 25, 'plateau_window': 20})

    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        if df.empty or len(df) < 5:
            return self._empty_signal("Insufficient data")

        close = df['close']
        volume = df['volume']
        current_price = float(close.iloc[-1])

        # EMA crossover
        ema_fast = TechnicalAnalysis.fast_ema(close, BotConfig.MOMENTUM_EMA_FAST)
        ema_slow = TechnicalAnalysis.fast_ema(close, BotConfig.MOMENTUM_EMA_SLOW)
        current_ema_fast = float(ema_fast.iloc[-1]) if not pd.isna(ema_fast.iloc[-1]) else current_price
        current_ema_slow = float(ema_slow.iloc[-1]) if not pd.isna(ema_slow.iloc[-1]) else current_price
        ema_cross = current_ema_fast > current_ema_slow

        # Price growth detection
        gcp_config = BotConfig.MOMENTUM_GCP_CONFIG[symbol]
        growth_window = gcp_config['growth_window']
        plateau_window = gcp_config['plateau_window']
        recent_growth = close.iloc[-growth_window:]
        recent_plateau = close.iloc[-plateau_window:]
        growth_pct = ((recent_growth.iloc[-1] / recent_growth.iloc[0] - 1) * 100)
        plateau_range = ((recent_plateau.max() / recent_plateau.min() - 1) * 100)

        volume_avg = volume.rolling(10).mean().iloc[-1] if len(volume) >= 10 else volume.iloc[-1]
        volume_surge = float(volume.iloc[-1]) > float(volume_avg) * BotConfig.MOMENTUM_VOLUME_MULTIPLIER

        confidence = 0.0
        action = 'hold'
        reason = 'No signal'

        # BUY SIGNAL
        if (growth_pct > BotConfig.MOMENTUM_MIN_PRICE_CHANGE and
            plateau_range < 0.5 and
            ema_cross and
            volume_surge):

            base_confidence = BotConfig.MOMENTUM_BASE_CONFIDENCE
            trend_bonus = BotConfig.MOMENTUM_TREND_CONFIDENCE_BONUS if growth_pct > 0.5 else 0
            volume_bonus = 0.1 if volume_surge else 0
            confidence = min(0.9, base_confidence + trend_bonus + volume_bonus)
            action = 'buy'
            reason = f'Quick-Momentum BUY: Growth={growth_pct:.2f}%, Plateau={plateau_range:.2f}%'

        # SELL SIGNAL
        elif (growth_pct < -BotConfig.MOMENTUM_MIN_PRICE_CHANGE and
              plateau_range < 0.5 and
              not ema_cross and
              volume_surge):

            base_confidence = BotConfig.MOMENTUM_BASE_CONFIDENCE
            trend_bonus = BotConfig.MOMENTUM_TREND_CONFIDENCE_BONUS if growth_pct < -0.5 else 0
            volume_bonus = 0.1 if volume_surge else 0
            confidence = min(0.9, base_confidence + trend_bonus + volume_bonus)
            action = 'sell'
            reason = f'Quick-Momentum SELL: Decline={abs(growth_pct):.2f}%, Plateau={plateau_range:.2f}%'

        if confidence < BotConfig.MOMENTUM_MIN_CONFIDENCE:
            action = 'hold'
            reason = f'Confidence too low: {confidence:.2f}'
            confidence = 0.0

        # Set stop loss and take profit
        atr = TechnicalAnalysis.calculate_atr(df['high'], df['low'], df['close'], period=BotConfig.MOMENTUM_ATR_PERIOD)
        current_atr = float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else 0.0

        if action == 'buy':
            stop_loss = current_price - current_atr * BotConfig.MOMENTUM_ATR_MULTIPLIER_SL
            take_profit = current_price + current_atr * BotConfig.MOMENTUM_ATR_MULTIPLIER_TP
        elif action == 'sell':
            stop_loss = current_price + current_atr * BotConfig.MOMENTUM_ATR_MULTIPLIER_SL
            take_profit = current_price - current_atr * BotConfig.MOMENTUM_ATR_MULTIPLIER_TP
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
            'growth': growth_pct,
            'plateau_range': plateau_range,
            'ema_cross': ema_cross,
            'volume_surge': volume_surge
        }
