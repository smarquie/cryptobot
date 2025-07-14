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
import eth_account
from eth_account.signers.local import LocalAccount

class ExchangeInterface:
    def __init__(self, mode: str = 'live', private_key: Optional[str] = None):
        self.mode = mode
        self.private_key = private_key
        self.symbols = BotConfig.TRADING_SYMBOLS
        self.hyperliquid_info = None
        self.hyperliquid_exchange = None
        self.account_address = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize exchange client based on mode"""
        if self.mode == 'backtest':
            print("🧪 Backtest mode: Using simulated data")
            return

        elif self.mode in ['paper', 'live']:
            testnet = (self.mode == 'paper')
            base_url = constants.TESTNET_API_URL if testnet else constants.MAINNET_API_URL

            try:
                # Initialize read-only info first
                self.hyperliquid_info = HLInfo(base_url=base_url, skip_ws=True)

                # Only initialize trading if private key provided
                if self.private_key and self.private_key.strip():
                    wallet = eth_account.Account.from_key(self.private_key)
                    self.account_address = wallet.address
                    self.hyperliquid_exchange = HLExchange(wallet, base_url, account_address=self.account_address)
                    print(f"✅ Trading enabled for Hyperliquid {'Testnet' if testnet else 'Mainnet'}")
                    print(f"👛 Wallet Address: {self.account_address}")
                else:
                    print("ℹ️ Read-only connection - no private key provided")

            except Exception as e:
                raise RuntimeError(f"❌ Failed to connect to Hyperliquid ({'testnet' if testnet else 'mainnet'}): {e}")
        else:
            raise ValueError(f"Invalid mode: {self.mode}. Use 'backtest', 'paper', or 'live'")

    def set_private_key(self, private_key: str):
        """Set private key dynamically after initialization"""
        if not private_key or not private_key.strip():
            print("❌ Cannot set empty private key")
            return False

        testnet = (self.mode == 'paper')
        base_url = constants.TESTNET_API_URL if testnet else constants.MAINNET_API_URL

        try:
            wallet = eth_account.Account.from_key(private_key)
            self.account_address = wallet.address
            self.hyperliquid_exchange = HLExchange(wallet, base_url, account_address=self.account_address)
            print(f"🔑 Private key set for wallet: {self.account_address}")
            return True
        except Exception as e:
            print(f"❌ Failed to set private key: {e}")
            return False

    def get_market_data(self) -> Dict[str, float]:
        """Get current prices for all symbols"""
        if self.mode in ['paper', 'live']:
            try:
                all_mids = self.hyperliquid_info.all_mids()
                return {symbol: all_mids.get(symbol, 0.0) for symbol in self.symbols if symbol in all_mids}
            except Exception as e:
                print(f"❌ Failed to fetch market  {e}")
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
                candles = self.hyperliquid_info.candles_snapshot(coin=symbol, interval=interval)
                df = pd.DataFrame(candles)
                df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
                df[['open', 'high', 'low', 'close']] = df[['o', 'h', 'l', 'c']].astype(float)
                df = df[['timestamp', 'open', 'high', 'low', 'close']].sort_values('timestamp').reset_index(drop=True)
                return df[-lookback:] if len(df) > lookback else df
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
            print("❌ Exchange not initialized for live/paper mode or missing private key")
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
        """Generate realistic fake candle data when API fails"""
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
