# utils/exchange.py

from hyperliquid.info import Info
from hyperliquid.exchange import Exchange as HLExchange
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import time
import random
from config import BotConfig

from hyperliquid.info import Info
from hyperliquid.exchange import Exchange as HLExchange
from coinbase.rest import RESTClient
import pandas as pd
from typing import Dict, Optional

class ExchangeInterface:
    def __init__(self, mode: str = 'live'):
        self.mode = mode
        self.client = None
        self.symbols = []

        if mode in ['paper', 'live']:
            # Use Hyperliquid for live/paper
            testnet = (mode == 'paper')
            base_url = "https://api.hyperliquid.testnet.xyz " if testnet else "https://api.hyperliquid.xyz "
            
            try:
                self.hyperliquid_info = Info(base_url=base_url)
                self.hyperliquid_exchange = HLExchange(wallet=None, info=self.hyperliquid_info)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Hyperliquid connection: {e}")
        elif mode == 'backtest':
            # Use Coinbase for backtest
            self.client = RESTClient(api_key="dummy", api_secret="dummy", api_passphrase="dummy")

    def get_market_data(self) -> Dict[str, float]:
        if self.mode in ['paper', 'live']:
            return self.hyperliquid_info.all_mids()
        elif self.mode == 'backtest':
            return {
                symbol.split('-')[0]: float(self.client.get_best_bid_ask(product_id=symbol)['bid'])
                for symbol in ['BTC-USDT', 'ETH-USDT', 'SOL-USDT']
            }

    def get_candles_df(self, symbol: str, interval: str = '1m', lookback: int = 30) -> pd.DataFrame:
        if self.mode in ['paper', 'live']:
            # Get real data from Hyperliquid (you may need to implement this)
            pass
        elif self.mode == 'backtest':
            # Get historical data from Coinbase
            raw_data = self.client.get_candlesticks(product_id=symbol, granularity=interval, limit=lookback)
            df = pd.DataFrame(raw_data['candles'], columns=['start', 'low', 'high', 'open', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['start'].astype(int), unit='s')
            df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
            return df.sort_values('timestamp').reset_index(drop=True)
        return pd.DataFrame()

class Portfolio:
    def __init__(self):
        self.positions = {}
        self.balance = BotConfig.PAPER_INITIAL_BALANCE

    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions

    def calculate_position_size(self, signal: Dict, entry_price: float) -> float:
        portfolio_value = self.balance + sum(p.size * p.entry_price for p in self.positions.values())
        risk_amount = portfolio_value * BotConfig.RISK_PER_TRADE
        risk_per_unit = abs(entry_price - signal['stop_loss'])
        return risk_amount / risk_per_unit

    def open_position(self, signal: Dict, symbol: str, price: float) -> bool:
        # Implement actual opening logic
        return True

    def get_summary(self) -> Dict:
        return {
            'balance': self.balance,
            'total_value': self.balance,
            'open_positions': len(self.positions)
        }

# ==================== HYPERLIQUID EXCHANGE INTERFACE ====================
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange as HLExchange
from typing import Dict, Any, Optional
import pandas as pd

class HyperliquidExchange:
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        try:
            self.hyperliquid_info = Info(testnet=testnet)
            self.hyperliquid_exchange = HLExchange(wallet=None, testnet=testnet)
            print(f"✅ Connected to Hyperliquid {'Testnet' if testnet else 'Mainnet'}")
        except Exception as e:
            raise RuntimeError(f"❌ Failed to initialize Hyperliquid exchange: {e}")

    def get_market_data(self) -> Dict[str, float]:
        """Get current mid prices"""
        try:
            return self.hyperliquid_info.all_mids()
        except Exception as e:
            print(f"❌ Failed to fetch market data: {e}")
            return {}

    def place_order(self, symbol: str, action: str, size: float, reduce_only: bool = False) -> Optional[Dict]:
        """Place a market order via Hyperliquid"""
        is_buy = action.lower() == 'buy'
        try:
            result = self.hyperliquid_exchange.submit_order(
                symbol=symbol,
                is_buy=is_buy,
                sz=str(size),
                order_type={'type': 'market'},  # ← Clean format
                reduce_only=reduce_only
            )
            print(f"📈 {action.upper()} order placed: {symbol} x {size}")
            return result
        except Exception as e:
            print(f"❌ Failed to place order: {e}")
            return None

    def get_candles_df(self, symbol: str, interval: str = '1m', lookback: int = 30) -> pd.DataFrame:
        """Fetch OHLCV data from Hyperliquid"""
        try:
            raw_data = self.hyperliquid_info.get_candles(symbol, interval, lookback * 60_000)  # Convert minutes to ms
            df = pd.DataFrame(raw_data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
            return df.sort_values('timestamp').reset_index(drop=True)
        except Exception as e:
            print(f"❌ Error fetching candles: {e}")
            return pd.DataFrame()

# ==================== COINBASE BACKTESTING INTERFACE ====================
class CoinbaseExchange:
    def __init__(self, api_key: str = "", secret: str = "", passphrase: str = ""):
        # Placeholder for real Coinbase SDK
        pass

    def get_candles_df(self, symbol: str, interval: str = '1m', lookback: int = 30) -> pd.DataFrame:
        if self.mode in ['paper', 'live']:
            # Real-time candles via Hyperliquid
            raw_data = self.hyperliquid_info.get_candles(symbol=symbol, interval=interval, limit=lookback)
            df = pd.DataFrame(raw_data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df.sort_values('timestamp').reset_index(drop=True)
    
        elif self.mode == 'backtest':
            # Use Binance or Coinbase for historical data
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval={interval}&limit={lookback}"
            response = requests.get(url).json()
            df = pd.DataFrame(response, columns=['timestamp', 'open', 'high', 'low', 'close', ...])
            df[['open', 'high', 'low', 'close']] = df[[...]].astype(float)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df.sort_values('timestamp').reset_index(drop=True)

    def get_market_data(self) -> Dict[str, float]:
        """Get current prices for all symbols in config"""
        from config import BotConfig
        if self.mode == 'backtest':
            # Simulated market data
            return {
                symbol: np.random.uniform(
                    self._get_price_range(symbol)[0],
                    self._get_price_range(symbol)[1]
                )
                for symbol in BotConfig.TRADING_SYMBOLS
            }
    
        elif self.mode in ['paper', 'live']:
            try:
                return self.hyperliquid_info.all_mids()
            except Exception as e:
                print(f"❌ Hyperliquid API error: {e}")
                return {}
    
    def _get_price_range(self, symbol: str):
        ranges = {
            'BTC': (58000, 62000),
            'ETH': (1700, 3000),
            'SOL': (100, 200),
            'AVAX': (10, 100),  # Example for AVAX
            'DOGE': (0.05, 0.15),
            'XRP': (0.4, 0.8),
            # Add more as needed
        }
        return ranges.get(symbol, (10, 1000))  # Default fallback range
