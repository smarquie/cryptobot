# utils/exchange.py

from coinbase.rest import RESTClient
import pandas as pd
from datetime import datetime, timedelta
import time

class CoinbaseExchange:
    def __init__(self, api_key: str, secret_key: str, passphrase: str):
        self.client = RESTClient(api_key=api_key, api_secret=secret_key, api_passphrase=passphrase)
        self.product_ids = []

    def get_market_data(self) -> dict:
        """Get current prices for all symbols"""
        return {
            symbol.split('-')[0]: float(self.client.get_best_bid_ask(product_id=symbol)['bid'])
            for symbol in self.product_ids
        }

    def get_candles_df(self, product_id: str, interval: str = 'ONE_MINUTE', lookback: int = 30) -> pd.DataFrame:
        """
        Fetch historical candles from Coinbase
        Supported intervals:
        ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, THIRTY_MINUTE,
        ONE_HOUR, TWO_HOUR, SIX_HOUR, TWENTY_FOUR_HOUR
        """
        granularity_map = {
            '1m': 'ONE_MINUTE',
            '5m': 'FIVE_MINUTE',
            '15m': 'FIFTEEN_MINUTE',
            '1h': 'ONE_HOUR'
        }
        granularity = granularity_map.get(interval, 'ONE_MINUTE')

        raw_data = self.client.get_candlesticks(product_id=product_id, granularity=granularity, limit=lookback)
        df = pd.DataFrame(raw_data['candles'], columns=[
            'start', 'low', 'high', 'open', 'close', 'volume'
        ])
        df['timestamp'] = pd.to_datetime(df['start'].astype(int), unit='s')
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        return df.sort_values('timestamp').reset_index(drop=True)

    def place_order(self, product_id: str, side: str, size: float, price: float = None, order_type: str = 'market'):
        """
        Place a market order on Coinbase
        Only market orders supported in this version
        """
        if order_type == 'market':
            response = self.client.market_order(
                client_oid=f"bot_{int(time.time())}",
                product_id=product_id,
                side=side.upper(),
                size=str(size)
            )
            return response
        else:
            raise NotImplementedError("Only market orders are supported")
