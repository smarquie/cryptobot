#!/usr/bin/env python3
"""
CENTRALIZED CONFIG.PY - ALL TRADING PARAMETERS
Comprehensive configuration with all parameters moved from strategy files
"""

class BotConfig:
    """
    🎯 CENTRALIZED TRADING PARAMETERS
    All strategy parameters moved from individual files to here
    """
    
    # ==================== BASIC SETTINGS ====================
    
    # Trading pairs
    TRADING_SYMBOLS = ["BTC", "AVAX", "SOL"]
    MODE = "paper"
    PAPER_INITIAL_BALANCE = 10000
    INITIAL_BALANCE = 10000
    CYCLE_INTERVAL = 60
    
    # ==================== SIGNAL GENERATION ====================
    
    MIN_CONFIDENCE = 0.2
    MAX_POSITIONS_PER_SYMBOL = 2
    
    # ==================== RISK MANAGEMENT ====================
    
    POSITION_SIZE_PERCENT = 10.0
    MAX_RISK_PERCENT = 2.0
    DEFAULT_STOP_LOSS_PERCENT = 0.5
    DEFAULT_TAKE_PROFIT_PERCENT = 1.0
    
    # ==================== ULTRA-SCALP STRATEGY PARAMETERS ====================
    
    # RSI Parameters
    ULTRA_SCALP_RSI_PERIOD = 7
    ULTRA_SCALP_RSI_OVERSOLD = 40
    ULTRA_SCALP_RSI_OVERBOUGHT = 60
    
    # SMA Parameters
    ULTRA_SCALP_SMA_PERIOD = 5
    
    # Momentum Parameters
    ULTRA_SCALP_RSI_SLOPE_THRESHOLD = -1.0
    ULTRA_SCALP_PRICE_CHANGE_THRESHOLD = -0.5
    
    # Risk Management
    ULTRA_SCALP_STOP_LOSS_PERCENT = 0.25
    ULTRA_SCALP_TAKE_PROFIT_PERCENT = 0.50
    ULTRA_SCALP_MAX_HOLD_SECONDS = 600
    
    # Confidence Calculation
    ULTRA_SCALP_BASE_CONFIDENCE = 0.5
    ULTRA_SCALP_RSI_DISTANCE_DIVISOR = 20
    ULTRA_SCALP_MOMENTUM_BONUS_MAX = 0.2
    ULTRA_SCALP_VOLUME_BONUS = 0.1
    
    # ==================== FAST-SCALP STRATEGY PARAMETERS ====================
    
    # RSI Parameters
    FAST_SCALP_RSI_PERIOD = 7
    FAST_SCALP_RSI_OVERSOLD = 40
    FAST_SCALP_RSI_OVERBOUGHT = 60
    
    # MACD Parameters
    FAST_SCALP_MACD_FAST = 5
    FAST_SCALP_MACD_SLOW = 10
    FAST_SCALP_MACD_SIGNAL = 4
    
    # Momentum Parameters
    FAST_SCALP_PRICE_CHANGE_THRESHOLD = -1.0
    
    # Volume Parameters
    FAST_SCALP_VOLUME_AVERAGE_PERIOD = 10
    FAST_SCALP_VOLUME_SURGE_MULTIPLIER = 1.05
    
    # Risk Management
    FAST_SCALP_STOP_LOSS_PERCENT = 0.20
    FAST_SCALP_TAKE_PROFIT_PERCENT = 0.40
    FAST_SCALP_MAX_HOLD_SECONDS = 900
    
    # Confidence Calculation
    FAST_SCALP_BASE_CONFIDENCE = 0.6
    FAST_SCALP_RSI_DISTANCE_DIVISOR = 20
    FAST_SCALP_MACD_BONUS_MAX = 0.2
    FAST_SCALP_VOLUME_BONUS = 0.2
    
    # ==================== QUICK-MOMENTUM STRATEGY PARAMETERS ====================
    
    # RSI Parameters
    QUICK_MOMENTUM_RSI_PERIOD = 7
    QUICK_MOMENTUM_RSI_BUY_THRESHOLD = 55
    QUICK_MOMENTUM_RSI_SELL_THRESHOLD = 45
    
    # Moving Average Parameters
    QUICK_MOMENTUM_FAST_MA_PERIOD = 3
    QUICK_MOMENTUM_SLOW_MA_PERIOD = 8
    
    # Momentum Parameters
    QUICK_MOMENTUM_MOMENTUM_THRESHOLD = 0.02
    
    # Risk Management
    QUICK_MOMENTUM_STOP_LOSS_PERCENT = 0.20
    QUICK_MOMENTUM_TAKE_PROFIT_PERCENT = 0.40
    QUICK_MOMENTUM_MAX_HOLD_SECONDS = 1800
    
    # Confidence Calculation
    QUICK_MOMENTUM_BASE_CONFIDENCE = 0.5
    QUICK_MOMENTUM_RSI_DISTANCE_DIVISOR = 20
    QUICK_MOMENTUM_MOMENTUM_BONUS_MAX = 0.3
    
    # ==================== TTM-SQUEEZE STRATEGY PARAMETERS ====================
    
    # RSI Parameters
    TTM_SQUEEZE_RSI_PERIOD = 7
    
    # Bollinger Bands Parameters
    TTM_SQUEEZE_BB_PERIOD = 20
    TTM_SQUEEZE_BB_STD_DEV = 2.0
    
    # Keltner Channels Parameters
    TTM_SQUEEZE_KC_PERIOD = 20
    TTM_SQUEEZE_KC_ATR_MULTIPLIER = 1.5
    
    # Momentum Parameters
    TTM_SQUEEZE_MOMENTUM_PERIOD = 20
    TTM_SQUEEZE_MOMENTUM_THRESHOLD = 0.3
    
    # CVD Parameters
    TTM_SQUEEZE_CVD_THRESHOLD = 0.2
    
    # Risk Management
    TTM_SQUEEZE_STOP_LOSS_PERCENT = 0.15
    TTM_SQUEEZE_TAKE_PROFIT_PERCENT = 0.20
    TTM_SQUEEZE_MAX_HOLD_SECONDS = 1200
    
    # Confidence Calculation
    TTM_SQUEEZE_BASE_CONFIDENCE = 0.6
    TTM_SQUEEZE_SQUEEZE_BONUS = 0.2
    TTM_SQUEEZE_MOMENTUM_BONUS_MAX = 0.2
    TTM_SQUEEZE_CVD_BONUS_MAX = 0.2
    
    # ==================== VOLUME ANALYSIS ====================
    
    VOLUME_SURGE_THRESHOLD = 1.01
    VOLUME_AVERAGE_PERIOD = 5
    
    # ==================== MOMENTUM ANALYSIS ====================
    
    RSI_SLOPE_MIN = -3.0
    RSI_SLOPE_MAX = 3.0
    PRICE_CHANGE_MIN = -2.0
    PRICE_CHANGE_MAX = 2.0
    
    # ==================== CONFIDENCE CALCULATION ====================
    
    # Base confidence levels
    ULTRA_SCALP_BASE_CONFIDENCE = 0.5
    FAST_SCALP_BASE_CONFIDENCE = 0.4
    QUICK_MOMENTUM_BASE_CONFIDENCE = 0.3
    TTM_SQUEEZE_BASE_CONFIDENCE = 0.4
    
    # Bonus multipliers
    RSI_DISTANCE_BONUS = 0.3
    MOMENTUM_BONUS = 0.3
    VOLUME_BONUS = 0.1
    
    # ==================== DATA COLLECTION ====================
    
    DATA_COLLECTION_ENABLED = True
    INITIAL_DATA_COLLECTION_MINUTES = 20
    DATA_VALIDATION_ENABLED = True
    MIN_DATA_POINTS = 5
    MAX_DATA_AGE_SECONDS = 300
    
    # ==================== SIGNAL AGGREGATION ====================
    
    SIGNAL_AGGREGATION_ENABLED = True
    MIN_STRATEGY_AGREEMENT = 1
    
    # ==================== POSITION MANAGEMENT ====================
    
    AUTO_CLOSE_POSITIONS = True
    MAX_POSITION_AGE_HOURS = 24
    
    # ==================== RISK MANAGEMENT ====================
    
    MAX_DAILY_LOSS_PERCENT = 5.0
    MAX_TOTAL_RISK_PERCENT = 10.0
    
    # ==================== TELEGRAM NOTIFICATIONS ====================
    
    TELEGRAM_ENABLED = True
    TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
    NOTIFY_ALL_SIGNALS = True
    NOTIFY_TRADES = True
    NOTIFY_ERRORS = True
    
    # ==================== LOGGING ====================
    
    LOG_LEVEL = "INFO"
    LOG_TO_FILE = True
    LOG_FILE_PATH = "trading_bot.log"
    
    # ==================== API SETTINGS ====================
    
    EXCHANGE_NAME = "coinbase"
    API_KEY = "YOUR_API_KEY_HERE"
    API_SECRET = "YOUR_API_SECRET_HERE"
    PASSPHRASE = "YOUR_PASSPHRASE_HERE"
    
    # ==================== BACKTESTING ====================
    
    BACKTEST_START_DATE = "2024-01-01"
    BACKTEST_END_DATE = "2024-12-31"
    BACKTEST_INITIAL_BALANCE = 10000
    
    # ==================== DEBUG SETTINGS ====================
    
    DEBUG_MODE = True
    DRY_RUN = True
    SIMULATE_TRADES = True
    ENABLE_PERFORMANCE_MONITORING = True
    LOG_PERFORMANCE_METRICS = True

    # ==================== POSITION SIZING LIMITS ====================
    MIN_POSITION_VALUE = 10      # Minimum position value in USD (example)
    MAX_POSITION_VALUE = 10000   # Maximum position value in USD (example)
    TARGET_POSITION_VALUE = 1000 # Target position value in USD (example)

    # ==================== STRATEGY PARAMETERS ====================
    # Ultra-Scalp Strategy (already present)
    # Fast-Scalp Strategy
    FAST_SCALP_EMA_FAST = 8
    FAST_SCALP_EMA_SLOW = 21
    # Quick-Momentum Strategy
    QUICK_MOMENTUM_STOCH_PERIOD = 14
    QUICK_MOMENTUM_MACD_FAST = 12
    QUICK_MOMENTUM_MACD_SLOW = 26
    QUICK_MOMENTUM_MACD_SIGNAL = 9
    # TTM-Squeeze Strategy
    TTM_SQUEEZE_BB_STD = 2.0
    TTM_SQUEEZE_KC_MULTIPLIER = 1.5
    # (all other parameters remain as previously defined)

# Export the config class
__all__ = ['BotConfig'] 
