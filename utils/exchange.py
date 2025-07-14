# utils/exchange.py

from hyperliquid.info import Info as HLInfo
from hyperliquid.exchange import Exchange as HLExchange
from hyperliquid.utils import constants
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import time
import random
from config import BotConfig

market_data = info.all_mids()
print("Available symbols:", market_data.keys())

class ExchangeInterface:
    def __init__(self, mode: str = 'live'):
        self.mode = mode
        self.symbols = BotConfig.TRADING_SYMBOLS
        self.hyperliquid_info = None
        self.hyperliquid_exchange = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize exchange client based on mode"""
        if self.mode == 'backtest':
            print("🧪 Backtest mode: Using simulated data")
            return
    
        elif self.mode in ['paper', 'live']:
            testnet = (self.mode == 'paper')
            base_url = constants.TESTNET_API_URL if testnet else constants.MAINNET_API_URL
            base_url = base_url.strip()
    
            try:
                # Use the correct initialization for the new SDK
                self.hyperliquid_info = HLInfo(base_url=base_url, skip_ws=True)
                self.hyperliquid_exchange = HLExchange(wallet=None, testnet=testnet)  # ← This is now correct
                print(f"✅ Connected to Hyperliquid {'Testnet' if testnet else 'Mainnet'}")
            except Exception as e:
                raise RuntimeError(f"❌ Failed to connect to Hyperliquid ({'testnet' if testnet else 'mainnet'}): {e}")
        else:
            raise ValueError(f"Invalid mode: {self.mode}. Use 'backtest', 'paper', or 'live'")

    def get_market_data(self) -> Dict[str, float]:
        """Get current prices for all symbols"""
        if self.mode in ['paper', 'live']:
            try:
                return self.hyperliquid_info.all_mids()
            except Exception as e:
                print(f"❌ Failed to fetch market  {e}")
                return {}
        elif self.mode == 'backtest':
            return {
                symbol: np.random.uniform(*self._get_price_range(symbol))
                for symbol in self.symbols
            }

    def get_candles_df(self, symbol: str, interval: str = '1m', lookback: int = 30) -> pd.DataFrame:
        """Fetch OHLCV data from Hyperliquid or simulate it"""
        if self.mode in ['paper', 'live']:
            try:
                raw_data = self.hyperliquid_info.candles_snapshot(coin=symbol, interval=interval)
                df = pd.DataFrame(raw_data)
                df['timestamp'] = pd.to_datetime(df['T'], unit='ms')
                df[['open', 'high', 'low', 'close', 'volume']] = df[['o', 'h', 'l', 'c', 'v']].astype(float)
                return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].sort_values('timestamp').reset_index(drop=True)
            except Exception as e:
                print(f"❌ Error fetching real candles: {e}")
                return self._generate_fallback_candles(symbol, lookback)

        elif self.mode == 'backtest':
            return self._generate_fallback_candles(symbol, lookback)

    def place_order(self, symbol: str, action: str, size: float, reduce_only: bool = False) -> Optional[Dict]:
        """Place market order via Hyperliquid"""
        if self.mode == 'backtest':
            print(f"[Backtest] Would have placed {action} order for {symbol} x {size}")
            return {"status": "simulated", "action": action, "size": size}
    
        if not self.hyperliquid_exchange:
            print("❌ Exchange not initialized for live/paper mode")
            return None
    
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

    def _generate_fallback_candles(self, symbol: str, lookback: int = 30) -> pd.DataFrame:
        """Generate realistic fake candle data when real API fails"""
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

    def _get_price_range(self, symbol: str):
        ranges = {
            'BTC': (58000, 62000),
            'ETH': (1700, 3000),
            'SOL': (100, 200),
            'AVAX': (10, 100),
            'DOGE': (0.05, 0.15),
            'XRP': (0.4, 0.8),
        }
        return ranges.get(symbol, (10, 1000))  # Default fallback range
