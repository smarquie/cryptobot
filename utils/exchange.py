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
            self.hyperliquid_info = Info(testnet=(mode == 'paper'))
            self.hyperliquid_exchange = HLExchange(self.hyperliquid_info)
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
class HyperliquidExchange:
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        self.hyperliquid_info = Info(testnet=testnet)
        self.hyperliquid_exchange = HLExchange(wallet=None, testnet=testnet)

    def get_market_data(self) -> Dict[str, float]:
        return self.hyperliquid_info.all_mids()

    def place_order(self, symbol: str, action: str, size: float, reduce_only: bool = False) -> Optional[Dict]:
        is_buy = action.lower() == 'buy'
        try:
            result = self.hyperliquid_exchange.submit_order(symbol=symbol, is_buy=is_buy, sz=str(size), order_type={'type': 'limit', 'isMarket': True}, reduce_only=reduce_only)
            print(f"📈 {action.upper()} order placed on Hyperliquid: {symbol} x {size}")
            return result
        except Exception as e:
            print(f"❌ Order failed: {e}")
            return None

# ==================== COINBASE BACKTESTING INTERFACE ====================
class CoinbaseExchange:
    def __init__(self, api_key: str = "", secret: str = "", passphrase: str = ""):
        # Placeholder for real Coinbase SDK
        pass

    def get_candles_df(self, symbol: str, interval: str = "1m", lookback: int = 30) -> pd.DataFrame:
        """Generate fake OHLCV data for backtest"""
        now = int(time.time()) * 1000
        timestamps = [now - (lookback - i) * 60_000 for i in range(lookback)]
        prices = np.random.normal(60000, 1000, lookback)
        opens = prices * np.random.uniform(0.995, 1.005, lookback)
        highs = prices * np.random.uniform(1.000, 1.005, lookback)
        lows = prices * np.random.uniform(0.995, 1.000, lookback)
        closes = prices
        volumes = np.random.uniform(1, 100, lookback)

        df = pd.DataFrame({
            'timestamp': pd.to_datetime([ts / 1000 for ts in timestamps], unit='s'),
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': volumes
        })
        return df

    def get_market_data(self) -> Dict[str, float]:
        """Return simulated market data for backtest"""
        return {
            'BTC': np.random.uniform(58000, 62000),
            'ETH': np.random.uniform(1700, 3000),
            'SOL': np.random.uniform(100, 200)
        }
