# strategies/fast_scalp.py

from .base import Strategy
from config import BotConfig
from utils.ta import TechnicalAnalysis

class FastScalpStrategy(Strategy):
    def __init__(self):
        super().__init__("Fast-Scalp")

    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        if df.empty or len(df) < BotConfig.MIN_DATA_MINUTES:
            return self._empty_signal("Insufficient data")

        close = df['close']
        volume = df['volume']
        current_price = float(close.iloc[-1])

        # RSI
        rsi = TechnicalAnalysis.calculate_rsi(close, BotConfig.FAST_SCALP_RSI_PERIOD)
        current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0

        # MACD
        config = BotConfig.FAST_SCALP_MACD_CONFIG.get(symbol, BotConfig.FAST_SCALP_MACD_CONFIG['BTC'])
        macd_line, signal_line, histogram = TechnicalAnalysis.calculate_macd(close, config['fast'], config['slow'], config['signal'])
        current_histogram = float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else 0.0
        current_macd = float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else 0.0
        current_signal = float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else 0.0

        # Volume surge
        volume_avg = volume.rolling(10).mean().iloc[-1] if len(volume) >= 10 else volume.iloc[-1]
        volume_surge = float(volume.iloc[-1]) > float(volume_avg) * BotConfig.FAST_SCALP_VOLUME_MULTIPLIER

        price_change_1m = ((current_price / close.iloc[-2] - 1) * 100) if len(close) > 1 else 0

        confidence = 0.0
        action = 'hold'
        reason = 'No signal'

        # BUY SIGNAL
        if (current_rsi < BotConfig.FAST_SCALP_RSI_BUY_THRESHOLD and
            current_histogram > BotConfig.FAST_SCALP_MACD_HISTOGRAM_THRESHOLD and
            current_macd > current_signal and
            abs(price_change_1m) > BotConfig.FAST_SCALP_PRICE_CHANGE_THRESHOLD and
            volume_surge):

            base_confidence = BotConfig.FAST_SCALP_BASE_CONFIDENCE
            rsi_bonus = min(0.15, (BotConfig.FAST_SCALP_RSI_BUY_THRESHOLD - current_rsi) / 30)
            macd_bonus = min(0.1, max(0, current_histogram / 0.5))
            momentum_bonus = min(0.1, abs(current_macd - current_signal) / current_signal * 100)
            volume_bonus = 0.1 if volume_surge else 0.0
            confidence = min(0.95, base_confidence + rsi_bonus + macd_bonus + momentum_bonus + volume_bonus)
            action = 'buy'
            reason = f'Fast-Scalp BUY: RSI={current_rsi:.1f}, MACD={current_histogram:.2f}%, Price change={price_change_1m:.2f}%'

        # SELL SIGNAL
        elif (current_rsi > BotConfig.FAST_SCALP_RSI_SELL_THRESHOLD and
              current_histogram < BotConfig.FAST_SCALP_MACD_HISTOGRAM_THRESHOLD and
              current_macd < current_signal and
              abs(price_change_1m) > BotConfig.FAST_SCALP_PRICE_CHANGE_THRESHOLD and
              volume_surge):

            base_confidence = BotConfig.FAST_SCALP_BASE_CONFIDENCE
            rsi_bonus = min(0.15, (current_rsi - BotConfig.FAST_SCALP_RSI_SELL_THRESHOLD) / 30)
            macd_bonus = min(0.1, max(0, abs(current_histogram) / 0.5))
            momentum_bonus = min(0.1, abs(current_macd - current_signal) / current_signal * 100)
            volume_bonus = 0.1 if volume_surge else 0.0
            confidence = min(0.95, base_confidence + rsi_bonus + macd_bonus + momentum_bonus + volume_bonus)
            action = 'sell'
            reason = f'Fast-Scalp SELL: RSI={current_rsi:.1f}, MACD={current_histogram:.2f}%, Price change={price_change_1m:.2f}%'

        # Set stop loss and take profit
        atr = TechnicalAnalysis.calculate_atr(df['high'], df['low'], df['close'], period=BotConfig.FAST_SCALP_ATR_PERIOD)
        current_atr = float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else 0.0

        if action == 'buy':
            stop_loss = current_price - current_atr * BotConfig.FAST_SCALP_ATR_MULTIPLIER_SL
            take_profit = current_price + current_atr * BotConfig.FAST_SCALP_ATR_MULTIPLIER_TP
        elif action == 'sell':
            stop_loss = current_price + current_atr * BotConfig.FAST_SCALP_ATR_MULTIPLIER_SL
            take_profit = current_price - current_atr * BotConfig.FAST_SCALP_ATR_MULTIPLIER_TP
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
            'macd_histogram': current_histogram,
            'price_change_1m': price_change_1m,
            'volume_surge': volume_surge
        }
