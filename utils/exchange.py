# utils/exchange.py

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
