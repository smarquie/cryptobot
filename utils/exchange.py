# utils/exchange.py

from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
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
    def __init__(self, mode: str = 'live', private_key: str = None):
        self.mode = mode
        self.symbols = BotConfig.TRADING_SYMBOLS
        self.hyperliquid_info = None
        self.hyperliquid_exchange = None
        self.private_key = private_key
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
                # Initialize Info client (doesn't require private key)
                self.hyperliquid_info = Info(base_url=base_url, skip_ws=True)
                
                # Initialize Exchange client (requires private key for trading)
                if self.private_key:
                    # Create wallet from private key
                    wallet = eth_account.Account.from_key(self.private_key)
                    self.hyperliquid_exchange = Exchange(wallet, base_url, account_address=wallet.address)
                else:
                    print("⚠️ No private key provided - Info functions only (no trading)")
                    
                print(f"✅ Connected to Hyperliquid {'Testnet' if testnet else 'Mainnet'}")
                
            except Exception as e:
                raise RuntimeError(f"❌ Failed to connect to Hyperliquid ({'testnet' if testnet else 'mainnet'}): {e}")
        else:
            raise ValueError(f"Invalid mode: {self.mode}. Use 'backtest', 'paper', or 'live'")

    def get_market_data(self) -> Dict[str, float]:
        """Get current prices for all symbols"""
        if self.mode in ['paper', 'live']:
            try:
                all_mids = self.hyperliquid_info.all_mids()
                # Filter to only our symbols
                return {symbol: all_mids.get(symbol, 0.0) for symbol in self.symbols if symbol in all_mids}
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
                # Note: Hyperliquid uses different interval format - convert if needed
                interval_map = {
                    '1m': '1m',
                    '5m': '5m', 
                    '15m': '15m',
                    '1h': '1h',
                    '4h': '4h',
                    '1d': '1d'
                }
                hl_interval = interval_map.get(interval, '1m')
                
                # Request recent candles
                candles = self.hyperliquid_info.candles_snapshot(
                    coin=symbol,
                    interval=hl_interval,
                    startTime=int((time.time() - lookback * 60) * 1000),  # lookback minutes
                    endTime=int(time.time() * 1000)
                )
                
                if candles and len(candles) > 0:
                    df = pd.DataFrame(candles)
                    # Hyperliquid returns: t (time), o (open), h (high), l (low), c (close), v (volume)
                    df = df.rename(columns={
                        't': 'timestamp',
                        'o': 'open', 
                        'h': 'high',
                        'l': 'low',
                        'c': 'close',
                        'v': 'volume'
                    })
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
                    return df.sort_values('timestamp').reset_index(drop=True)
                else:
                    print(f"❌ No candle data returned for {symbol}")
                    return self._generate_fallback_candles(symbol, lookback)
                    
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

        try:
            # Use market_open for opening positions or market_close for closing
            if reduce_only:
                # For closing positions, use market_close
                result = self.hyperliquid_exchange.market_close(symbol)
            else:
                # For opening positions, use market_open
                result = self.hyperliquid_exchange.market_open(
                    coin=symbol,
                    is_buy=is_buy,
                    sz=size,
                    px=None,  # None for market order
                    slippage=0.05  # 5% slippage tolerance
                )
            
            if result and result.get("status") == "ok":
                print(f"📈 {action.upper()} order placed: {symbol} x {size}")
                return result
            else:
                print(f"❌ Order failed: {result}")
                return None
                
        except Exception as e:
            print(f"❌ Order failed: {e}")
            return None

    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if self.mode == 'backtest':
            return {"mode": "backtest", "balance": 10000}
            
        if not self.hyperliquid_info:
            return {}
            
        try:
            if self.hyperliquid_exchange:
                user_state = self.hyperliquid_info.user_state(self.hyperliquid_exchange.wallet.address)
                return user_state
            else:
                return {"error": "No wallet address available"}
        except Exception as e:
            print(f"❌ Failed to get account info: {e}")
            return {}

    def get_open_orders(self) -> list:
        """Get open orders"""
        if self.mode == 'backtest':
            return []
            
        if not self.hyperliquid_info or not self.hyperliquid_exchange:
            return []
            
        try:
            return self.hyperliquid_info.open_orders(self.hyperliquid_exchange.wallet.address)
        except Exception as e:
            print(f"❌ Failed to get open orders: {e}")
            return []

    def cancel_order(self, symbol: str, order_id: int) -> Optional[Dict]:
        """Cancel specific order"""
        if self.mode == 'backtest':
            print(f"[Backtest] Would have cancelled order {order_id}")
            return {"status": "simulated"}
            
        if not self.hyperliquid_exchange:
            print("❌ Exchange not initialized")
            return None
            
        try:
            result = self.hyperliquid_exchange.cancel(symbol, order_id)
            print(f"🚫 Cancelled order {order_id}")
            return result
        except Exception as e:
            print(f"❌ Failed to cancel order: {e}")
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
        """Price ranges for simulation"""
        ranges = {
            'BTC': (58000, 62000),
            'ETH': (1700, 3000),
            'SOL': (100, 200),
            'AVAX': (10, 100),
            'DOGE': (0.05, 0.15),
            'XRP': (0.4, 0.8),
        }
        return ranges.get(symbol, (10, 1000))  # Default fallback range
