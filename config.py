#!/usr/bin/env python3
"""
CENTRALIZED CONFIG.PY - ALL TRADING PARAMETERS
Well-organized configuration with parameters grouped by strategy
"""

class BotConfig:
    """
    🎯 CENTRALIZED TRADING PARAMETERS
    All parameters organized by strategy for easy management
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
    
    # ==================== POSITION SIZING LIMITS ====================
    
    POSITION_SIZE_PERCENT = 10.0
    MAX_RISK_PERCENT = 2.0
    DEFAULT_STOP_LOSS_PERCENT = 0.5
    DEFAULT_TAKE_PROFIT_PERCENT = 1.0
    
    MIN_POSITION_VALUE = 10      # Minimum position value in USD
    MAX_POSITION_VALUE = 10000   # Maximum position value in USD
    TARGET_POSITION_VALUE = 1000 # Target position value in USD
    
    # ==================== ULTRA-SCALP STRATEGY - ALL PARAMETERS ====================
    
    # RSI Parameters
    ULTRA_SCALP_RSI_PERIOD = 7
    ULTRA_SCALP_RSI_OVERSOLD = 40
    ULTRA_SCALP_RSI_OVERBOUGHT = 60
    ULTRA_SCALP_RSI_BUY_THRESHOLD = 40
    ULTRA_SCALP_RSI_SELL_THRESHOLD = 60
    ULTRA_SCALP_RSI_CONFIDENCE_FACTOR = 20
    
    # SMA Parameters
    ULTRA_SCALP_SMA_PERIOD = 5
    
    # Momentum Parameters
    ULTRA_SCALP_RSI_SLOPE_THRESHOLD = -1.0
    ULTRA_SCALP_PRICE_CHANGE_THRESHOLD = -0.5
    
    # Risk Management
    ULTRA_SCALP_STOP_LOSS_PERCENT = 0.25
    ULTRA_SCALP_TAKE_PROFIT_PERCENT = 0.50
    ULTRA_SCALP_MAX_HOLD_SECONDS = 600
    ULTRA_SCALP_STOP_LOSS = 0.25
    ULTRA_SCALP_PROFIT_TARGET = 0.50
    
    # Confidence Calculation
    ULTRA_SCALP_BASE_CONFIDENCE = 0.5
    ULTRA_SCALP_RSI_DISTANCE_DIVISOR = 20
    ULTRA_SCALP_MOMENTUM_BONUS_MAX = 0.2
    ULTRA_SCALP_VOLUME_BONUS = 0.1
    
    # Dynamic Risk Management
    DYNAMIC_ULTRA_SCALP_SL = 0.25  # 0.25% stop loss
    DYNAMIC_ULTRA_SCALP_TP = 0.50  # 0.50% take profit
    
    # ==================== FAST-SCALP STRATEGY - ALL PARAMETERS ====================
    
    # RSI Parameters
    FAST_SCALP_RSI_PERIOD = 7
    FAST_SCALP_RSI_OVERSOLD = 40
    FAST_SCALP_RSI_OVERBOUGHT = 60
    FAST_SCALP_RSI_BUY_THRESHOLD = 40
    FAST_SCALP_RSI_SELL_THRESHOLD = 60
    
    # MACD Parameters
    FAST_SCALP_MACD_FAST = 5
    FAST_SCALP_MACD_SLOW = 10
    FAST_SCALP_MACD_SIGNAL = 4
    FAST_SCALP_EMA_FAST = 8
    FAST_SCALP_EMA_SLOW = 21
    
    # Momentum Parameters
    FAST_SCALP_PRICE_CHANGE_THRESHOLD = -1.0
    
    # Volume Parameters
    FAST_SCALP_VOLUME_AVERAGE_PERIOD = 10
    FAST_SCALP_VOLUME_SURGE_MULTIPLIER = 1.05
    FAST_SCALP_VOLUME_PERIOD = 10
    FAST_SCALP_VOLUME_MULTIPLIER = 1.05
    FAST_SCALP_VOLUME_CONFIDENCE_BONUS = 0.2
    
    # Risk Management
    FAST_SCALP_STOP_LOSS_PERCENT = 0.20
    FAST_SCALP_TAKE_PROFIT_PERCENT = 0.40
    FAST_SCALP_MAX_HOLD_SECONDS = 900
    FAST_SCALP_STOP_LOSS = 0.20
    FAST_SCALP_PROFIT_TARGET = 0.40
    
    # Confidence Calculation
    FAST_SCALP_BASE_CONFIDENCE = 0.6
    FAST_SCALP_RSI_DISTANCE_DIVISOR = 20
    FAST_SCALP_MACD_BONUS_MAX = 0.2
    FAST_SCALP_VOLUME_BONUS = 0.2
    
    # Dynamic Risk Management
    DYNAMIC_FAST_SCALP_SL = 0.30  # 0.30% stop loss
    DYNAMIC_FAST_SCALP_TP = 0.60  # 0.60% take profit
    
    # ==================== QUICK-MOMENTUM STRATEGY - ALL PARAMETERS ====================
    
    # RSI Parameters
    QUICK_MOMENTUM_RSI_PERIOD = 7
    QUICK_MOMENTUM_RSI_BUY_THRESHOLD = 55
    QUICK_MOMENTUM_RSI_SELL_THRESHOLD = 45
    
    # Moving Average Parameters
    QUICK_MOMENTUM_FAST_MA_PERIOD = 3
    QUICK_MOMENTUM_SLOW_MA_PERIOD = 8
    QUICK_MOMENTUM_STOCH_PERIOD = 14
    
    # MACD Parameters
    QUICK_MOMENTUM_MACD_FAST = 12
    QUICK_MOMENTUM_MACD_SLOW = 26
    QUICK_MOMENTUM_MACD_SIGNAL = 9
    
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
    
    # Dynamic Risk Management
    DYNAMIC_QUICK_MOMENTUM_SL = 0.40  # 0.40% stop loss
    DYNAMIC_QUICK_MOMENTUM_TP = 0.80  # 0.80% take profit
    
    # ==================== TTM-SQUEEZE STRATEGY - ALL PARAMETERS ====================
    
    # RSI Parameters
    TTM_SQUEEZE_RSI_PERIOD = 7
    
    # Bollinger Bands Parameters
    TTM_SQUEEZE_BB_PERIOD = 20
    TTM_SQUEEZE_BB_STD_DEV = 2.0
    TTM_BB_PERIOD = 20  # Bollinger Bands period
    TTM_BB_STDDEV = 2.0  # Bollinger Bands standard deviation
    TTM_SQUEEZE_BB_STD = 2.0
    
    # Keltner Channels Parameters
    TTM_SQUEEZE_KC_PERIOD = 20
    TTM_SQUEEZE_KC_ATR_MULTIPLIER = 1.5
    TTM_KC_PERIOD = 20  # Keltner Channel period
    TTM_KC_ATR_MULTIPLIER = 1.5  # Keltner Channel ATR multiplier
    TTM_SQUEEZE_KC_MULTIPLIER = 1.5
    
    # Momentum Parameters
    TTM_SQUEEZE_MOMENTUM_PERIOD = 20
    TTM_SQUEEZE_MOMENTUM_THRESHOLD = 0.3
    TTM_MOMENTUM_PERIOD = 20  # Momentum calculation period
    TTM_MOMENTUM_THRESHOLD = 0.5  # Minimum momentum for entry
    
    # CVD Parameters
    TTM_SQUEEZE_CVD_THRESHOLD = 0.2
    TTM_CVD_LOOKBACK = 20  # CVD calculation lookback
    TTM_CVD_DIVERGENCE_THRESHOLD = 0.7  # CVD divergence threshold
    TTM_CVD_MOMENTUM_THRESHOLD = 0.3  # Minimum CVD momentum for entry
    
    # Squeeze Parameters
    TTM_MIN_SQUEEZE_PERIODS = 3  # Minimum periods in squeeze before entry
    
    # Risk Management
    TTM_SQUEEZE_STOP_LOSS_PERCENT = 0.15
    TTM_SQUEEZE_TAKE_PROFIT_PERCENT = 0.20
    TTM_SQUEEZE_MAX_HOLD_SECONDS = 1200
    TTM_MAX_HOLD_SECONDS = 1200  # 20 minutes max hold
    TTM_PROFIT_TARGET = 0.003  # Profit target (0.30%)
    TTM_STOP_LOSS = 0.002  # Stop loss (0.20%)
    
    # Confidence Calculation
    TTM_SQUEEZE_BASE_CONFIDENCE = 0.6
    TTM_SQUEEZE_SQUEEZE_BONUS = 0.2
    TTM_SQUEEZE_MOMENTUM_BONUS_MAX = 0.2
    TTM_SQUEEZE_CVD_BONUS_MAX = 0.2
    TTM_BASE_CONFIDENCE = 0.6  # Base confidence level
    TTM_SQUEEZE_CONFIDENCE_BONUS = 0.2  # Bonus for strong squeeze
    TTM_CVD_CONFIDENCE_BONUS = 0.2  # Bonus for CVD confirmation
    TTM_MIN_CONFIDENCE = 0.5  # Minimum confidence to trade
    
    # Dynamic Risk Management
    DYNAMIC_TTM_SQUEEZE_SL = 0.50  # 0.50% stop loss
    DYNAMIC_TTM_SQUEEZE_TP = 1.00  # 1.00% take profit
    
    # ==================== MOMENTUM STRATEGY - ALL PARAMETERS ====================
    
    # RSI Parameters
    MOMENTUM_RSI_BUY_THRESHOLD = 55
    MOMENTUM_RSI_SELL_THRESHOLD = 45
    
    # Moving Average Parameters
    MOMENTUM_FAST_MA_PERIOD = 3
    MOMENTUM_SLOW_MA_PERIOD = 8
    
    # Momentum Parameters
    MOMENTUM_TREND_PERIODS = 10
    MOMENTUM_MIN_PRICE_CHANGE = 0.02
    
    # Risk Management
    MOMENTUM_MAX_HOLD_SECONDS = 1800  # 30 minutes
    MOMENTUM_STOP_LOSS = 0.20
    MOMENTUM_PROFIT_TARGET = 0.40
    
    # Confidence Calculation
    MOMENTUM_BASE_CONFIDENCE = 0.5
    MOMENTUM_TREND_CONFIDENCE_BONUS = 0.2
    
    # ==================== GLOBAL DYNAMIC RISK MANAGEMENT ====================
    
    DYNAMIC_STOP_LOSS_PERCENT = 0.5  # 0.5% stop loss
    DYNAMIC_TAKE_PROFIT_PERCENT = 1.0  # 1.0% take profit
    
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
    MIN_DATA_MINUTES = 20  # Minimum data minutes for analysis
    
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
    HYPERLIQUID_PRIVATE_KEY = "YOUR_PRIVATE_KEY_HERE"
    
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

# Export the config class
__all__ = ['BotConfig'] 
