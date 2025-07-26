# !/usr/bin/env python3
"""
CONFIG.PY - TRADING PARAMETERS
Replacement for GitHub repository - FIXED VERSION
Based on working code with permissive parameters
Maintains BotConfig structure for compatibility
"""

class BotConfig:
    """
    🎯 CENTRALIZED TRADING PARAMETERS
    Adjust these values to change trading behavior
    All strategy logic uses these parameters
    """
    
    # ==================== BASIC SETTINGS ====================
    
    # Trading pairs (add/remove as needed)
    TRADING_SYMBOLS = ["BTC", "AVAX", "SOL"]  # Can add: "AVAX", "MATIC", etc.
    
    # Trading mode and initial balance
    MODE = "paper"  # 'paper', 'live', 'backtest'
    PAPER_INITIAL_BALANCE = 10000
    INITIAL_BALANCE = 10000  # FIXED: Added missing attribute
    
    # ==================== TRADING CYCLE ====================
    
    # Trading cycle interval (seconds)
    CYCLE_INTERVAL = 60  # FIXED: Added missing attribute - 1 minute cycles
    
    # ==================== SIGNAL GENERATION ====================
    
    # Minimum confidence for any signal (0.0 to 1.0)
    MIN_CONFIDENCE = 0.2  # FIXED: Much lower than GitHub (0.4-0.5)
    
    # Maximum number of concurrent positions per symbol
    MAX_POSITIONS_PER_SYMBOL = 4

    # ==================== RISK MANAGEMENT ====================
    
    # Position sizing (percentage of available balance)
    POSITION_SIZE_PERCENT = 25.0  # 10% of balance per trade
    
    # Position sizing limits
    MIN_POSITION_VALUE = 1000.0  # Minimum $1,000 per trade
    MAX_POSITION_VALUE = 3500.0  # Maximum $3,500 per trade (35% of $10k)
    TARGET_POSITION_VALUE = 2500.0  # Target $2,500 per trade (25% of $10k)
    
    # Maximum total risk per trade (percentage)
    MAX_RISK_PERCENT = 2.0  # 2% max risk per trade
    
    # Stop loss and take profit defaults
    DEFAULT_STOP_LOSS_PERCENT = 0.5  # 0.5% stop loss
    DEFAULT_TAKE_PROFIT_PERCENT = 1.0  # 1.0% take profit
    
    # Stop loss and take profit defaults
    DEFAULT_STOP_LOSS_PERCENT = 0.25  # 0.5% stop loss
    DEFAULT_TAKE_PROFIT_PERCENT = 0.60  # 1.0% take profit
    
    # ==================== DATA COLLECTION ====================
    
    # Data collection settings (preserved from GitHub)
    DATA_COLLECTION_ENABLED = True
    INITIAL_DATA_COLLECTION_MINUTES = 20  # FIXED: Keep 20-minute requirement
    DATA_VALIDATION_ENABLED = True
    MIN_DATA_MINUTES = 30  # FIXED: Added missing attribute for data collection
    
    # ==================== STRATEGY PARAMETERS ====================
    
    # Ultra-Scalp Strategy
    ULTRA_SCALP_RSI_PERIOD = 7
    ULTRA_SCALP_SMA_PERIOD = 5
    ULTRA_SCALP_RSI_BUY_THRESHOLD = 35      # RSI oversold threshold
    ULTRA_SCALP_RSI_SELL_THRESHOLD = 65     # RSI overbought threshold
    ULTRA_SCALP_BASE_CONFIDENCE = 0.5
    ULTRA_SCALP_RSI_CONFIDENCE_FACTOR = 10
    ULTRA_SCALP_MIN_CONFIDENCE = 0.2
    ULTRA_SCALP_PROFIT_TARGET = 0.0060       # 0.50% profit target
    ULTRA_SCALP_STOP_LOSS = 0.0025           # 0.20% stop loss
    ULTRA_SCALP_MAX_HOLD_SECONDS = 600       # 10 minutes
    
    # Fast-Scalp Strategy
    FAST_SCALP_RSI_PERIOD = 14
    FAST_SCALP_EMA_FAST = 8
    FAST_SCALP_EMA_SLOW = 21
    FAST_SCALP_RSI_BUY_THRESHOLD = 40        # RSI oversold threshold
    FAST_SCALP_RSI_SELL_THRESHOLD = 50       # RSI overbought threshold
    FAST_SCALP_MACD_FAST = 5
    FAST_SCALP_MACD_SLOW = 10
    FAST_SCALP_MACD_SIGNAL = 4
    FAST_SCALP_VOLUME_MULTIPLIER = 1.05      # Volume surge threshold
    FAST_SCALP_VOLUME_PERIOD = 10
    FAST_SCALP_BASE_CONFIDENCE = 0.4
    FAST_SCALP_VOLUME_CONFIDENCE_BONUS = 0.2
    FAST_SCALP_MIN_CONFIDENCE = 0.2
    FAST_SCALP_PROFIT_TARGET = 0.0060
    FAST_SCALP_STOP_LOSS = 0.0025
    FAST_SCALP_MAX_HOLD_SECONDS = 900        # 15 minutes
    
    # Quick-Momentum Strategy (Golden Cross Pattern Detection)
    QUICK_MOMENTUM_SHORT_EMA_PERIOD = 5    # Short EMA for GCP detection
    QUICK_MOMENTUM_MEDIUM_EMA_PERIOD = 10  # Medium EMA for GCP detection  
    QUICK_MOMENTUM_LONG_EMA_PERIOD = 20    # Long EMA for GCP detection
    QUICK_MOMENTUM_GCP_MIN_MOMENTUM = 0.5  # Minimum momentum for GCP confirmation
    QUICK_MOMENTUM_GCP_CONFIDENCE_THRESHOLD = 0.2  # GCP pattern confidence threshold
    QUICK_MOMENTUM_MIN_CONFIDENCE = 0.2  # Overall strategy confidence threshold
    QUICK_MOMENTUM_MAX_HOLD_SECONDS = 1200  # 20 minutes
    
    # TTM-Squeeze Strategy
    TTM_SQUEEZE_RSI_PERIOD = 14
    TTM_SQUEEZE_BB_PERIOD = 20
    TTM_SQUEEZE_BB_STD = 2.0
    TTM_SQUEEZE_KC_PERIOD = 20
    TTM_SQUEEZE_KC_MULTIPLIER = 1.5
    TTM_SQUEEZE_RSI_BUY_THRESHOLD = 40  # RSI oversold threshold
    TTM_SQUEEZE_RSI_SELL_THRESHOLD = 60  # RSI overbought threshold
    TTM_SQUEEZE_MIN_CONFIDENCE = 0.2  # FIXED: Much lower (was 0.4)
    TTM_SQUEEZE_MAX_HOLD_SECONDS = 1800  # 30 minutes
    
    # ==================== VOLUME ANALYSIS ====================
    
    # Volume surge thresholds (much more permissive)
    VOLUME_SURGE_THRESHOLD = 1.01  # FIXED: Much lower (was 1.2-1.5)
    VOLUME_AVERAGE_PERIOD = 5  # FIXED: Shorter period (was 10-20)
    
    # ==================== MOMENTUM ANALYSIS ====================
    
    # RSI slope thresholds (much more permissive)
    RSI_SLOPE_MIN = 0.0  # FIXED: Much more permissive (was -1.0)
    RSI_SLOPE_MAX = 0.0   # FIXED: Much more permissive (was 1.0)
    
    # Price change thresholds (much more permissive)
    PRICE_CHANGE_MIN = 0.0  # FIXED: Much more permissive (was -0.5)
    PRICE_CHANGE_MAX = 0.0   # FIXED: Much more permissive (was 0.5)
    
    # ==================== CONFIDENCE CALCULATION ====================
    
    # Base confidence levels (much higher)
    QUICK_MOMENTUM_BASE_CONFIDENCE = 0.3  # FIXED: Higher (was 0.2)
    TTM_SQUEEZE_BASE_CONFIDENCE = 0.4   # FIXED: Higher (was 0.3)
    
    # Bonus multipliers (much more generous)
    RSI_DISTANCE_BONUS = 0.3  # FIXED: Higher (was 0.1)
    MOMENTUM_BONUS = 0.3      # FIXED: Higher (was 0.1)
    VOLUME_BONUS = 0.1        # FIXED: Higher (was 0.05)
    
    # ==================== TELEGRAM NOTIFICATIONS ====================
    
    # Telegram settings
    TELEGRAM_ENABLED = True
    TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
    
    # Notification levels
    NOTIFY_ALL_SIGNALS = True
    NOTIFY_TRADES = True
    NOTIFY_ERRORS = True
    
    # ==================== LOGGING ====================
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_TO_FILE = True
    LOG_FILE_PATH = "trading_bot.log"
    
    # ==================== API SETTINGS ====================
    
    # Exchange API settings
    EXCHANGE_NAME = "coinbase"
    API_KEY = "YOUR_API_KEY_HERE"
    API_SECRET = "YOUR_API_SECRET_HERE"
    PASSPHRASE = "YOUR_PASSPHRASE_HERE"
    
    # ==================== BACKTESTING ====================
    
    # Backtesting settings
    BACKTEST_START_DATE = "2024-01-01"
    BACKTEST_END_DATE = "2024-12-31"
    BACKTEST_INITIAL_BALANCE = 10000
    
    # ==================== ADVANCED SETTINGS ====================
    
    # Data validation settings
    MIN_DATA_POINTS = 5  # FIXED: Much lower (was 20)
    MAX_DATA_AGE_SECONDS = 300  # 5 minutes
    
    # Signal aggregation settings
    SIGNAL_AGGREGATION_ENABLED = True
    MIN_STRATEGY_AGREEMENT = 1  # FIXED: Much lower (was 2)
    
    # Position management settings
    AUTO_CLOSE_POSITIONS = True
    MAX_POSITION_AGE_HOURS = 24
    
    # Risk management settings
    MAX_DAILY_LOSS_PERCENT = 5.0
    MAX_TOTAL_RISK_PERCENT = 10.0
    
    # ==================== DEBUG SETTINGS ====================
    
    # Debug and testing settings
    DEBUG_MODE = True
    DRY_RUN = True
    SIMULATE_TRADES = True
    
    # Performance monitoring
    ENABLE_PERFORMANCE_MONITORING = True
    LOG_PERFORMANCE_METRICS = True

# Export the config class
__all__ = ['BotConfig'] 
