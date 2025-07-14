# utils/exchange.py

from hyperliquid.info import Info
from hyperliquid.exchange import Exchange as HLExchange
from coinbase.rest import RESTClient as CoinbaseClient
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from config import BotConfig
import requests

class ExchangeInterface:
    def __init__(self, mode: str = 'live'):
        self.mode = mode
        self.symbols = BotConfig.TRADING_SYMBOLS
        self.client = None
        self.hyperliquid_info = None
        self.hyperliquid_exchange = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize exchange client based on trading mode"""
        if self.mode == 'backtest':
            print("🧪 Backtest mode: Using Coinbase/Binance historical data")
            self.client = CoinbaseClient(api_key="dummy", api_secret="dummy", passphrase="dummy")
        elif self.mode in ['paper', 'live']:
            testnet = (self.mode == 'paper')
            try:
                # Initialize Hyperliquid connection
                self.hyperliquid_info = Info(testnet=testnet)
                self.hyperliquid_exchange = HLExchange(wallet=None, testnet=testnet)
                print(f"🔌 Connected to Hyperliquid {'Testnet' if testnet else 'Mainnet'}")
            except Exception as e:
                raise RuntimeError(f"❌ Failed to connect to Hyperliquid: {e}")
        else:
            raise ValueError(f"Invalid mode: {self.mode}")

    def get_market_data(self) -> Dict[str, float]:
        """Get current prices for all configured symbols"""
        if self.mode in ['paper', 'live']:
            return self.hyperliquid_info.all_mids()
        elif self.mode == 'backtest':
            return {
                symbol: self._simulate_price(symbol)
                for symbol in self.symbols
            }

    def get_candles_df(self, symbol: str, interval: str = '1m', lookback: int = 30) -> pd.DataFrame:
        """Fetch OHLCV data for given symbol and timeframe"""
        if self.mode in ['paper', 'live']:
            try:
                raw_data = self.hyperliquid_info.get_candles(symbol, interval, lookback * 60_000)  # Convert minutes to ms
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
                raw_data = self.client.get_candlesticks(product_id=product_id, granularity=interval, limit=lookback)
                df = pd.DataFrame(raw_data['candles'], columns=['start', 'low', 'high', 'open', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['start'].astype(int), unit='s')
                df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
                return df.sort_values('timestamp').reset_index(drop=True)
            except Exception as e:
                print(f"❌ Coinbase API error for {symbol}: {e}")
                return pd.DataFrame()

        return pd.DataFrame()

    def place_order(self, symbol: str, action: str, size: float, price: float = None, reduce_only: bool = False) -> Optional[Dict]:
        """Place market order using Hyperliquid SDK"""
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

    def _simulate_price(self, symbol: str) -> float:
        """Simulate price for backtesting"""
        ranges = {
            'BTC': (58000, 62000),
            'ETH': (1700, 3000),
            'SOL': (100, 200),
            'AVAX': (10, 100),
            'DOGE': (0.05, 0.15),
            'XRP': (0.4, 0.8),
        }
        low, high = ranges.get(symbol, (10, 1000))
        return np.random.uniform(low, high)
        
