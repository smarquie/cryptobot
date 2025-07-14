# strategies/ultra_scalp.py

from .base import Strategy
from config import BotConfig
from utils.ta import TechnicalAnalysis

class UltraScalpStrategy(Strategy):
    def __init__(self):
        super().__init__("Ultra-Scalp")

    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        if df.empty or len(df) < BotConfig.MIN_DATA_MINUTES:
            return self._empty_signal("Insufficient data")

        close = df['close']
        volume = df['volume']
        current_price = float(close.iloc[-1])

        # Calculate indicators
        rsi = TechnicalAnalysis.calculate_rsi(close, BotConfig.ULTRA_SCALP_RSI_PERIOD)
        current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
        sma_long = TechnicalAnalysis.fast_sma(close, BotConfig.ULTRA_SCALP_SMA_LONG_PERIOD)
        current_sma = float(sma_long.iloc[-1]) if not pd.isna(sma_long.iloc[-1]) else current_price

        # RSI Slope calculation for reversal detection
        rsi_slope_reversal = False
        if len(rsi) >= 4:
            rsi_prev_2 = float(rsi.iloc[-4]) if not pd.isna(rsi.iloc[-4]) else current_rsi
            rsi_prev_1 = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
            slope1 = rsi_prev_1 - rsi_prev_2
            slope2 = current_rsi - rsi_prev_1
            if (slope1 < -0.5 and slope2 > 0.5) or (slope1 > 0.5 and slope2 < -0.5):
                rsi_slope_reversal = True

        price_change_1m = ((current_price / close.iloc[-2] - 1) * 100) if len(close) > 1 else 0
        volume_avg = volume.rolling(10).mean().iloc[-1] if len(volume) >= 10 else volume.iloc[-1]
        volume_surge = float(volume.iloc[-1]) > float(volume_avg) * BotConfig.ULTRA_SCALP_VOLUME_MULTIPLIER

        confidence = 0.0
        action = 'hold'
        reason = 'No signal'

        # BUY SIGNAL
        if (current_rsi < BotConfig.ULTRA_SCALP_RSI_BUY_THRESHOLD and
            rsi_slope_reversal and
            current_price > current_sma and
            abs(price_change_1m) > 0.3 and
            volume_surge):

            base_confidence = BotConfig.ULTRA_SCALP_BASE_CONFIDENCE
            rsi_distance = BotConfig.ULTRA_SCALP_RSI_BUY_THRESHOLD - current_rsi
            momentum_bonus = min(0.2, max(0, slope2 / 5 + price_change_1m / 100))
            volume_bonus = 0.1 if volume_surge else 0.0
            confidence = min(0.9, base_confidence + (rsi_distance / BotConfig.ULTRA_SCALP_RSI_CONFIDENCE_FACTOR) + momentum_bonus + volume_bonus)
            action = 'buy'
            reason = f'Ultra-Scalp BUY: RSI={current_rsi:.1f}(slope:{slope2:.1f}), momentum={price_change_1m:.2f}%'

        # SELL SIGNAL
        elif (current_rsi > BotConfig.ULTRA_SCALP_RSI_SELL_THRESHOLD and
              rsi_slope_reversal and
              current_price < current_sma and
              abs(price_change_1m) > 0.3 and
              volume_surge):

            base_confidence = BotConfig.ULTRA_SCALP_BASE_CONFIDENCE
            rsi_distance = current_rsi - BotConfig.ULTRA_SCALP_RSI_SELL_THRESHOLD
            momentum_bonus = min(0.2, max(0, abs(slope2) / 5 + abs(price_change_1m) / 100))
            volume_bonus = 0.1 if volume_surge else 0.0
            confidence = min(0.9, base_confidence + (rsi_distance / BotConfig.ULTRA_SCALP_RSI_CONFIDENCE_FACTOR) + momentum_bonus + volume_bonus)
            action = 'sell'
            reason = f'Ultra-Scalp SELL: RSI={current_rsi:.1f}(slope:{slope2:.1f}), momentum={price_change_1m:.2f}%'

        # Set stop loss and take profit
        atr = TechnicalAnalysis.calculate_atr(df['high'], df['low'], df['close'], period=BotConfig.ULTRA_SCALP_ATR_PERIOD)
        current_atr = float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else 0.0

        if action == 'buy':
            stop_loss = current_price - current_atr * BotConfig.ULTRA_SCALP_ATR_MULTIPLIER_SL
            take_profit = current_price + current_atr * BotConfig.ULTRA_SCALP_ATR_MULTIPLIER_TP
        elif action == 'sell':
            stop_loss = current_price + current_atr * BotConfig.ULTRA_SCALP_ATR_MULTIPLIER_SL
            take_profit = current_price - current_atr * BotConfig.ULTRA_SCALP_ATR_MULTIPLIER_TP
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
            'rsi': current_rsi,
            'rsi_slope': slope2 if len(rsi) >= 3 else 0,
            'price_change_1m': price_change_1m,
            'volume_surge': volume_surge
        }
