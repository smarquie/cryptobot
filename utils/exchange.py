# utils/exchange.py

from hyperliquid.info import Info as HLInfo
from hyperliquid.exchange import Exchange as HLExchange
from hyperliquid.utils import constants
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import random
from config import BotConfig

class ExchangeInterface:
    def __init__(self, mode: str = 'live', wallet: Optional[Any] = None):
        self.mode = mode
        self.symbols = BotConfig.TRADING_SYMBOLS
        self.wallet = wallet
        self.hyperliquid_info = None
        self.hyperliquid_exchange = None
        self.account_address = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize exchange client based on mode"""
        testnet = (self.mode == 'paper')
        base_url = constants.TESTNET_API_URL if testnet else constants.MAINNET_API_URL
        
        try:
            self.hyperliquid_info = HLInfo(base_url=base_url, skip_ws=True)
            
            if self.wallet:
                self.hyperliquid_exchange = HLExchange(self.wallet, base_url)
                self.account_address = self.wallet.address
                print(f"✅ Trading enabled for {self.account_address}")
            else:
                print("ℹ️ No private key provided – read-only connection")

        except Exception as e:
            raise RuntimeError(f"❌ Failed to connect to Hyperliquid: {e}")

    def get_market_data(self) -> Dict[str, float]:
        """Get current mid prices for all symbols"""
        if self.mode in ['paper', 'live']:
            try:
                mids = self.hyperliquid_info.all_mids()
                return {s: float(mids[s]) for s in self.symbols if s in mids}
            except Exception as e:
                print(f"❌ Failed to fetch market data: {e}")
                return {}
        elif self.mode == 'backtest':
            return {
                symbol: np.random.uniform(*self._get_price_range(symbol))
                for symbol in self.symbols
            }

    def get_candles_df(self, symbol: str, interval: str = '1m', lookback: int = 30) -> pd.DataFrame:
        """Fetch OHLCV data from Hyperliquid or simulate if unavailable"""
        if self.mode in ['paper', 'live']:
            try:
                raw_data = self.hyperliquid_info.candles_snapshot(coin=symbol, interval=interval)
                df = pd.DataFrame(raw_data)
                df['timestamp'] = pd.to_datetime(df['T'], unit='ms')
                df[['open', 'high', 'low', 'close']] = df[['o', 'h', 'l', 'c']].astype(float)
                return df[['timestamp', 'open', 'high', 'low', 'close']].sort_values('timestamp').reset_index(drop=True)
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
            print("❌ Exchange not initialized – missing private key?")
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
        """Generate simulated candle data when API fails"""
        market_data = self.get_market_data()
        current_price = market_data.get(symbol, 60000)

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

            candles_data.append({
                'timestamp': pd.to_datetime(timestamp, unit='ms'),
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': random.uniform(100, 1000)
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
