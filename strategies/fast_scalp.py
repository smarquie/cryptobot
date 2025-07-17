class FastScalpStrategy:
    """FIXED Fast-scalp strategy - MUCH MORE PERMISSIVE"""
    
    def __init__(self):
        self.name = "Fast-Scalp"
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        try:
            if df.empty or len(df) < 10:  # FIXED: Lower minimum
                return self._empty_signal('Insufficient data')

            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Calculate indicators using centralized parameters
            rsi = self._calculate_rsi(close, 7)  # RSI period
            macd_line, signal_line, histogram = self._calculate_macd(close, 5, 10, 4)
            volume_sma = self._fast_sma(volume, 10)
            
            current_price = float(close.iloc[-1])
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            current_macd = float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else 0.0
            current_signal = float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else 0.0
            current_volume = float(volume.iloc[-1])
            avg_volume = float(volume_sma.iloc[-1]) if not pd.isna(volume_sma.iloc[-1]) else current_volume
            
            # RSI Slope calculation
            rsi_slope = 0.0
            if len(rsi) >= 3:  # FIXED: Only need 3 periods
                rsi_prev = float(rsi.iloc[-3]) if not pd.isna(rsi.iloc[-3]) else current_rsi
                rsi_slope = current_rsi - rsi_prev
            
            # MACD momentum confirmation
            macd_momentum = 0.0
            if len(macd_line) >= 3:
                macd_prev = float(macd_line.iloc[-3]) if not pd.isna(macd_line.iloc[-3]) else current_macd
                macd_momentum = current_macd - macd_prev
            
            # Volume confirmation (FIXED: Made optional)
            volume_confirmed = current_volume > avg_volume * 1.1
            
            confidence = 0.0
            action = 'hold'
            reason = 'No signal'
            
            # FIXED BUY SIGNAL - MUCH MORE PERMISSIVE
            if (current_rsi < 40 and  # FIXED: 40 instead of 30
                # FIXED: Much more permissive MACD conditions
                (current_macd > current_signal or macd_momentum > -0.1)):  # Either MACD bullish OR not falling fast
                
                action = 'buy'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.6  # FIXED: Higher base confidence
                rsi_distance = 40 - current_rsi  # FIXED: Use 40 as threshold
                macd_bonus = min(0.2, max(0, (current_macd - current_signal) / 0.01))
                volume_bonus = 0.2 if volume_confirmed else 0.0  # FIXED: Volume is bonus, not requirement
                
                confidence = min(0.9, base_confidence + (rsi_distance / 20) + macd_bonus + volume_bonus)
                reason = f'FIXED Fast-scalp BUY: RSI={current_rsi:.1f}, MACD={current_macd:.4f}, Signal={current_signal:.4f}'
                
            # FIXED SELL SIGNAL - MUCH MORE PERMISSIVE
            elif (current_rsi > 60 and  # FIXED: 60 instead of 70
                  # FIXED: Much more permissive MACD conditions
                  (current_macd < current_signal or macd_momentum < 0.1)):  # Either MACD bearish OR not rising fast
                
                action = 'sell'
                
                # FIXED: More generous confidence calculation
                base_confidence = 0.6  # FIXED: Higher base confidence
                rsi_distance = current_rsi - 60  # FIXED: Use 60 as threshold
                macd_bonus = min(0.2, max(0, (current_signal - current_macd) / 0.01))
                volume_bonus = 0.2 if volume_confirmed else 0.0  # FIXED: Volume is bonus, not requirement
                
                confidence = min(0.9, base_confidence + (rsi_distance / 20) + macd_bonus + volume_bonus)
                reason = f'FIXED Fast-scalp SELL: RSI={current_rsi:.1f}, MACD={current_macd:.4f}, Signal={current_signal:.4f}'

            # Set stop loss and take profit using centralized parameters
            if action == 'buy':
                stop_loss = current_price * (1 - 0.0025)  # 0.25% stop loss
                take_profit = current_price * (1 + 0.0050)  # 0.50% profit target
            elif action == 'sell':
                stop_loss = current_price * (1 + 0.0025)  # 0.25% stop loss
                take_profit = current_price * (1 - 0.0050)  # 0.50% profit target
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
                'max_hold_time': 900,  # 15 minutes
                'target_hold': '15 minutes',
                'rsi': current_rsi,
                'macd': current_macd,
                'signal': current_signal,
                'volume_confirmed': volume_confirmed
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
    
    def _calculate_macd(self, data: pd.Series, fast: int, slow: int, signal: int) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD"""
        try:
            ema_fast = data.ewm(span=fast, adjust=False).mean()
            ema_slow = data.ewm(span=slow, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            histogram = macd_line - signal_line
            return macd_line, signal_line, histogram
        except Exception as e:
            return pd.Series([0] * len(data)), pd.Series([0] * len(data)), pd.Series([0] * len(data))
