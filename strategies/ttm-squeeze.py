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
        current_price = float(close.iloc[-1])

        # Bollinger Bands
        bb_period = BotConfig.TTM_BB_PERIOD
        bb_stddev = BotConfig.TTM_KC_ATR_MULTIPLIER
        sma = TA.fast_sma(close, bb_period)
        std = close.rolling(bb_period).std()
        bb_upper = sma + std * bb_stddev
        bb_lower = sma - std * bb_stddev

        # Keltner Channels
        atr = TA.calculate_atr(high, low, close, BotConfig.TTM_KC_PERIOD)
        midline = TA.fast_sma(close, BotConfig.TTM_KC_PERIOD)
        kc_upper = midline + BotConfig.TTM_KC_ATR_MULTIPLIER * atr
        kc_lower = midline - BotConfig.TTM_KC_ATR_MULTIPLIER * atr

        # CVD (Cumulative Volume Delta)
        cvd = (volume * (close - close.shift(1))).cumsum()
        cvd_momentum = ((cvd.iloc[-1] / cvd.iloc[-2] - 1) * 100) if len(cvd) >= 2 else 0.0

        # Squeeze detection
        squeeze_on = (bb_upper.iloc[-1] < kc_upper.iloc[-1]) or (bb_lower.iloc[-1] > kc_lower.iloc[-1])
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

        if recent_squeeze_count >= BotConfig.TTM_MIN_SQUEEZE_PERIODS and abs(momentum_normalized) > BotConfig.TTM_MOMENTUM_THRESHOLD:
            if momentum_normalized > 0:
                action = 'buy'
                reason = f'TTM-Squeeze BUY: Squeeze={recent_squeeze_count}, Momentum={momentum_normalized:.2f}%, CVD={cvd_momentum:.2f}%'
            else:
                action = 'sell'
                reason = f'TTM-Squeeze SELL: Squeeze={recent_squeeze_count}, Momentum={momentum_normalized:.2f}%, CVD={cvd_momentum:.2f}%'

            base_confidence = 0.5
            squeeze_bonus = 0.1 if recent_squeeze_count >= 3 else 0
            momentum_bonus = 0.1 if abs(momentum_normalized) > BotConfig.TTM_MOMENTUM_THRESHOLD * 1.5 else 0
            confidence = min(0.95, base_confidence + squeeze_bonus + momentum_bonus)

        if confidence < BotConfig.TTM_MIN_CONFIDENCE:
            action = 'hold'
            reason = f'Confidence too low: {confidence:.2f}'
            confidence = 0.0

        if action == 'buy':
            stop_loss = current_price * (1 - BotConfig.TTM_STOP_LOSS)
            take_profit = current_price * (1 + BotConfig.TTM_PROFIT_TARGET)
        elif action == 'sell':
            stop_loss = current_price * (1 + BotConfig.TTM_STOP_LOSS)
            take_profit = current_price * (1 - BotConfig.TTM_PROFIT_TARGET)
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
            'cvd_momentum': cvd_momentum
        }