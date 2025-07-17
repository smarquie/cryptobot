# strategies/ttm_squeeze.py

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base import Strategy
from config import BotConfig
from utils.ta import TechnicalAnalysis

class TTMSqueezeStrategy(Strategy):
    def __init__(self):
        super().__init__("TTM-Squeeze")
        self.squeeze_history = {}

    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        if df.empty or len(df) < BotConfig.MIN_DATA_MINUTES:
            return self._empty_signal("Insufficient data")

        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        current_price = float(close.iloc[-1])

        # Bollinger Bands
        bb_period = BotConfig.TTM_BB_PERIOD
        bb_stddev = BotConfig.TTM_KC_ATR_MULTIPLIER
        sma = TechnicalAnalysis.fast_sma(close, bb_period)
        std = close.rolling(bb_period).std()
        bb_upper = sma + std * bb_stddev
        bb_lower = sma - std * bb_stddev

        # Keltner Channels
        kc_period = BotConfig.TTM_KC_PERIOD
        atr = TechnicalAnalysis.calculate_atr(high, low, close, kc_period)
        midline = TechnicalAnalysis.fast_sma(close, kc_period)
        kc_upper = midline + BotConfig.TTM_KC_ATR_MULTIPLIER * atr
        kc_lower = midline - BotConfig.TTM_KC_ATR_MULTIPLIER * atr

        # Squeeze detection
        squeeze_on = float(bb_upper.iloc[-1]) < float(kc_upper.iloc[-1]) or float(bb_lower.iloc[-1]) > float(kc_lower.iloc[-1])
        if symbol not in self.squeeze_history:
            self.squeeze_history[symbol] = []
        self.squeeze_history[symbol].append(squeeze_on)
        self.squeeze_history[symbol] = self.squeeze_history[symbol][-10:]
        recent_squeeze_count = sum(1 for s in self.squeeze_history[symbol][-BotConfig.TTM_MIN_SQUEEZE_PERIODS:] if s)

        # Momentum
        momentum_delta = current_price - midline.iloc[-1]
        momentum_normalized = momentum_delta / current_price

        confidence = 0.0
        action = 'hold'
        reason = 'No signal'

        # BUY SIGNAL
        if recent_squeeze_count >= BotConfig.TTM_MIN_SQUEEZE_PERIODS and momentum_normalized > BotConfig.TTM_MOMENTUM_THRESHOLD:
            action = 'buy'
            reason = f'TTM-Squeeze BUY: Squeeze={recent_squeeze_count}, Momentum={momentum_normalized:.2f}%'
            base_confidence = 0.5
            squeeze_bonus = 0.1 if recent_squeeze_count >= 3 else 0
            momentum_bonus = 0.1 if abs(momentum_normalized) > BotConfig.TTM_MOMENTUM_THRESHOLD * 1.5 else 0
            confidence = min(0.95, base_confidence + squeeze_bonus + momentum_bonus)

        # SELL SIGNAL
        elif recent_squeeze_count >= BotConfig.TTM_MIN_SQUEEZE_PERIODS and momentum_normalized < -BotConfig.TTM_MOMENTUM_THRESHOLD:
            action = 'sell'
            reason = f'TTM-Squeeze SELL: Squeeze={recent_squeeze_count}, Momentum={momentum_normalized:.2f}%'
            base_confidence = 0.5
            squeeze_bonus = 0.1 if recent_squeeze_count >= 3 else 0
            momentum_bonus = 0.1 if abs(momentum_normalized) > BotConfig.TTM_MOMENTUM_THRESHOLD * 1.5 else 0
            confidence = min(0.95, base_confidence + squeeze_bonus + momentum_bonus)

        if confidence < BotConfig.TTM_MIN_CONFIDENCE:
            action = 'hold'
            reason = f'Confidence too low: {confidence:.2f}'
            confidence = 0.0

        # Set stop loss and take profit
        atr = TechnicalAnalysis.calculate_atr(high, low, close, period=BotConfig.TTM_ATR_PERIOD)
        current_atr = float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else 0.0

        if action == 'buy':
            stop_loss = current_price - current_atr * BotConfig.TTM_ATR_MULTIPLIER_SL
            take_profit = current_price + current_atr * BotConfig.TTM_ATR_MULTIPLIER_TP
        elif action == 'sell':
            stop_loss = current_price + current_atr * BotConfig.TTM_ATR_MULTIPLIER_SL
            take_profit = current_price - current_atr * BotConfig.TTM_ATR_MULTIPLIER_TP
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
            'squeeze_on': squeeze_on,
            'squeeze_count': recent_squeeze_count,
            'momentum': momentum_normalized,
        }
