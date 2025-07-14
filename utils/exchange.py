# utils/exchange.py

from hyperliquid.info import Info as HLInfo
from hyperliquid.exchange import Exchange as HLExchange
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import time
from config import BotConfig

class ExchangeInterface:
    def __init__(self, mode: str = 'live'):
        self.mode = mode
        self.symbols = BotConfig.TRADING_SYMBOLS
        self.hyperliquid_info = None
        self.hyperliquid_exchange = None
        self.client = None  # For backtest mode

        self._initialize_client()

    def _initialize_client(self):
        """Initialize exchange client based on trading mode"""
        if self.mode == 'backtest':
            print("🧪 Backtest mode: Using simulated data")
            return

        elif self.mode in ['paper', 'live']:
            testnet = (self.mode == 'paper')
            base_url = "https://api.hyperliquid.testnet.xyz " if testnet else "https://api.hyperliquid.xyz "
            print(f"🔌 Connecting to {'Testnet' if testnet else 'Mainnet'}: {base_url}")

            try:
                self.hyperliquid_info = HLInfo(base_url=base_url)
                self.hyperliquid_exchange = HLExchange(wallet=None, info=self.hyperliquid_info)
                print("✅ Connected to Hyperliquid")
            except Exception as e:
                raise RuntimeError(f"❌ Failed to connect to Hyperliquid ({'testnet' if testnet else 'mainnet'}): {e}")
        else:
            raise ValueError(f"Invalid mode: {self.mode}. Use 'backtest', 'paper', or 'live'")

    def get_market_data(self) -> Dict[str, float]:
        """Get current mid prices for all symbols"""
        if self.mode in ['paper', 'live']:
            try:
                return self.hyperliquid_info.all_mids()
            except Exception as e:
                print(f"❌ Failed to fetch market data: {e}")
                return {}
        elif self.mode == 'backtest':
            return {
                symbol: np.random.uniform(*self._get_price_range(symbol))
                for symbol in self.symbols
            }

    def get_candles_df(self, symbol: str, interval: str = '1m', lookback: int = 30) -> pd.DataFrame:
        """Fetch OHLCV data for given symbol and timeframe"""
        if self.mode in ['paper', 'live']:
            try:
                raw_data = self.hyperliquid_info.get_candles(symbol=symbol, interval=interval, limit=lookback)
                df = pd.DataFrame(raw_data, columns=['timestamp', 'open', 'high', 'low', 'close'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
                return df.sort_values('timestamp').reset_index(drop=True)
            except Exception as e:
                print(f"❌ Error fetching candles from Hyperliquid: {e}")
                return pd.DataFrame()

        elif self.mode == 'backtest':
            product_id = f"{symbol}-USDT"
            try:
                # Simulated Coinbase-style logic
                url = f"https://api.binance.com/api/v3/klines?symbol={product_id}&interval={interval}&limit={lookback}"
                response = requests.get(url).json()
                df = pd.DataFrame(response, columns=[
                    'timestamp', 'open', 'high', 'low', 'close',
                    'volume', 'close_time', 'quote_asset_volume',
                    'number_of_trades', 'taker_buy_base_vol', 'taker_buy_quote_vol'
                ])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                df = df.astype({'open': float, 'high': float, 'low': float, 'close': float, 'volume': float})
                return df
            except Exception as e:
                print(f"❌ Binance API error: {e}")
                return pd.DataFrame()

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
