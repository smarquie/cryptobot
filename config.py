# config.py

class BotConfig:
    # Mode: 'backtest', 'paper', or 'live'
    MODE = 'paper'

    # Trading symbols (Coinbase format)
    TRADING_SYMBOLS = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT']  # Product IDs on Coinbase

    # Risk parameters
    RISK_PER_TRADE = 0.02  # 2% per trade
    MAX_PORTFOLIO_EXPOSURE = 0.6  # Max 60% in open positions
    MAX_CONCURRENT_POSITIONS = 3
    MAX_POSITION_PCT = 0.2  # Max 20% per symbol
    MIN_POSITION_PCT = 0.05  # Min 5%

    # Strategy Parameters
    ULTRA_SCALP_RSI_PERIOD = 7
    ULTRA_SCALP_SMA_LONG_PERIOD = 20
    ULTRA_SCALP_RSI_BUY_THRESHOLD = 35
    ULTRA_SCALP_RSI_SELL_THRESHOLD = 65
    ULTRA_SCALP_STOP_LOSS = 0.0020
    ULTRA_SCALP_PROFIT_TARGET = 0.0040
    ULTRA_SCALP_MIN_CONFIDENCE = 0.2
    ULTRA_SCALP_VOLUME_MULTIPLIER = 1.2

    FAST_SCALP_MACD_CONFIG = {
        'BTC-USDT': {'fast': 8, 'slow': 21, 'signal': 5},
        'ETH-USDT': {'fast': 5, 'slow': 13, 'signal': 4},
        'SOL-USDT': {'fast': 3, 'slow': 8, 'signal': 3}
    }

    TTM_BB_PERIOD = 20
    TTM_KC_ATR_MULTIPLIER = 1.2
    TTM_MIN_SQUEEZE_PERIODS = 3
    TTM_STOP_LOSS = 0.002
    TTM_PROFIT_TARGET = 0.004

    MOMENTUM_EMA_FAST = 5
    MOMENTUM_EMA_SLOW = 10
    MOMENTUM_MIN_PRICE_CHANGE = 0.003  # 0.3%
    MOMENTUM_STOP_LOSS = 0.002
    MOMENTUM_PROFIT_TARGET = 0.004

    TIMEFRAME = '1m'
    CYCLE_INTERVAL = 1  # seconds

    # Telegram settings
    TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Replace this
    TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"      # Replace this
    TELEGRAM_ENABLED = True if TELEGRAM_BOT_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN" and TELEGRAM_CHAT_ID else False

    # Coinbase credentials
    COINBASE_API_KEY = "your_api_key"
    COINBASE_API_SECRET = "your_secret"
    COINBASE_PASSPHRASE = "your_passphrase"

    # Minimum data requirement
    MIN_DATA_MINUTES = 20
    DATA_VALIDATION_ENABLED = True