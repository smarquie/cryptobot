class UltraScalpStrategy(Strategy):
    def __init__(self):
        super().__init__("Ultra-Scalp")

    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        if df.empty or len(df) < BotConfig.MIN_DATA_MINUTES:
            return self._empty_signal("Insufficient data")

        close = df['close']
        volume = df['volume']
        current_price = float(close.iloc[-1])
        rsi = TA.calculate_rsi(close, BotConfig.ULTRA_SCALP_RSI_PERIOD)
        current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
        sma_long = TA.fast_sma(close, BotConfig.ULTRA_SCALP_SMA_LONG_PERIOD)
        current_sma = float(sma_long.iloc[-1]) if not pd.isna(sma_long.iloc[-1]) else current_price

        # RSI slope calculation (momentum confirmation)
        rsi_slope = 0.0
        if len(rsi) >= 3:
            rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
            rsi_slope = current_rsi - rsi_prev

        price_change_1m = ((current_price / close.iloc[-2] - 1) * 100) if len(close) > 1 else 0.0
        volume_avg = volume.rolling(10).mean().iloc[-1] if len(volume) >= 10 else volume.iloc[-1]
        volume_surge = float(volume.iloc[-1]) > float(volume_avg) * BotConfig.ULTRA_SCALP_VOLUME_MULTIPLIER

        confidence = 0.0
        action = 'hold'
        reason = 'No signal'

        # BUY SIGNAL
        if (current_rsi < BotConfig.ULTRA_SCALP_RSI_BUY_THRESHOLD and
            (rsi_slope > -1.0 or price_change_1m > -0.5) and
            current_price > current_sma and
            abs(price_change_1m) > 0.3 and
            volume_surge):

            base_confidence = BotConfig.ULTRA_SCALP_BASE_CONFIDENCE
            rsi_distance = BotConfig.ULTRA_SCALP_RSI_BUY_THRESHOLD - current_rsi
            momentum_bonus = min(0.2, max(0, rsi_slope / 10 + price_change_1m / 100))
            volume_bonus = 0.1 if volume_surge else 0.0
            confidence = min(0.9, base_confidence + (rsi_distance / BotConfig.ULTRA_SCALP_RSI_CONFIDENCE_FACTOR) + momentum_bonus + volume_bonus)
            action = 'buy'
            reason = f'Ultra-Scalp BUY: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_change_1m:.2f}%'

        # SELL SIGNAL
        elif (current_rsi > BotConfig.ULTRA_SCALP_RSI_SELL_THRESHOLD and
              (rsi_slope < 1.0 or price_change_1m < 0.5) and
              current_price < current_sma and
              abs(price_change_1m) > 0.3 and
              volume_surge):

            base_confidence = BotConfig.ULTRA_SCALP_BASE_CONFIDENCE
            rsi_distance = current_rsi - BotConfig.ULTRA_SCALP_RSI_SELL_THRESHOLD
            momentum_bonus = min(0.2, max(0, abs(rsi_slope) / 10 + abs(price_change_1m) / 100))
            volume_bonus = 0.1 if volume_surge else 0.0
            confidence = min(0.9, base_confidence + (rsi_distance / BotConfig.ULTRA_SCALP_RSI_CONFIDENCE_FACTOR) + momentum_bonus + volume_bonus)
            action = 'sell'
            reason = f'Ultra-Scalp SELL: RSI={current_rsi:.1f}(slope:{rsi_slope:.1f}), momentum={price_change_1m:.2f}%'

        # Set SL/TP
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
            'target_hold': f'{BotConfig.ULTRA_SCALP_MAX_HOLD_SECONDS // 60} minutes',
            'rsi': current_rsi,
            'rsi_slope': rsi_slope,
            'price_change_1m': price_change_1m,
            'volume_surge': volume_surge
        }