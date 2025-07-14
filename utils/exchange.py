# utils/exchange.py

import pandas as pd
import numpy as np
import time
import random
from typing import Dict, Any, Optional
from config import BotConfig

# Hyperliquid imports
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange as HLExchange
from hyperliquid.utils import constants

class ExchangeInterface:
    def __init__(self, mode: str = 'paper'):
        self.mode = mode
        self.symbols = BotConfig.TRADING_SYMBOLS
        self.base_url = constants.TESTNET_API_URL if mode == 'paper' else constants.MAINNET_API_URL
        self.skip_ws = True  # Skip WebSocket in Colab
        
        try:
            self.hyperliquid_info = Info(base_url=self.base_url, skip_ws=self.skip_ws)
            self.hyperliquid_exchange = HLExchange(wallet=None, info=self.hyperliquid_info)
            print(f"✅ Connected to Hyperliquid ({mode})")
        except Exception as e:
            raise RuntimeError(f"❌ Failed to connect to Hyperliquid: {e}")

    def get_market_data(self) -> Dict[str, float]:
        """Get current mid prices"""
        try:
            return self.hyperliquid_info.all_mids()
        except Exception as e:
            print(f"❌ Failed to fetch market data: {e}")
            return {}

    def get_candles_df(self, symbol: str, interval: str = '1m', lookback: int = 30) -> pd.DataFrame:
        """Fetch OHLCV data from Hyperliquid API"""
        try:
            candles = self.hyperliquid_info.candles_snapshot(coin=symbol, interval=interval)
            if not candles:
                raise Exception("Empty candle response")

            df = pd.DataFrame(candles)
            df['timestamp'] = pd.to_datetime(df['T'], unit='ms')
            df['open'] = df['o'].astype(float)
            df['high'] = df['h'].astype(float)
            df['low'] = df['l'].astype(float)
            df['close'] = df['c'].astype(float)
            df['volume'] = df['v'].astype(float)

            result_df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].sort_values('timestamp').reset_index(drop=True)
            return result_df[-lookback:] if len(result_df) > lookback else result_df
        except Exception as e:
            print(f"❌ Error fetching real candles: {e}")
            return self._generate_fallback_candles(symbol, lookback)

    def _generate_fallback_candles(self, symbol: str, lookback: int = 30) -> pd.DataFrame:
        """Generate simulated candles if real data fails"""
        market_data = self.get_market_data()
        current_price = float(market_data.get(symbol, 60000))
        candles_data = []
        base_price = current_price * 0.999
        current_time = int(time.time() * 1000)

        for i in range(lookback):
            timestamp = current_time - (lookback - i) * 60_000
            price_change = random.uniform(-0.002, 0.002)
            close_price = base_price * (1 + price_change)
            open_price = base_price
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.001))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.001))
            volume = random.uniform(100, 1000)

            candles_data.append({
                'timestamp': pd.to_datetime(timestamp, unit='ms'),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
            base_price = close_price

        return pd.DataFrame(candles_data)

    def place_order(self, symbol: str, action: str, size: float, reduce_only: bool = False) -> Optional[Dict]:
        """Place market order via Hyperliquid"""
        is_buy = action.lower() == 'buy'
        sz = str(size)

        try:
            result = self.hyperliquid_exchange.submit_order(
                symbol=symbol,
                is_buy=is_buy,
                sz=sz,
                order_type={'type': 'market'},
                reduce_only=reduce_only
            )
            print(f"📈 {action.upper()} order placed: {symbol} x {size}")
            return result
        except Exception as e:
            print(f"❌ Order failed: {e}")
            return None
