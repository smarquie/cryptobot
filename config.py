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
    ULTRA_SCALP_RSI_PERIOD = 14
    ULTRA_SCALP_SMA_PERIOD = 20
    ULTRA_SCALP_RSI_BUY_THRESHOLD = 30
    ULTRA_SCALP_RSI_SELL_THRESHOLD = 70
    ULTRA_SCALP_RSI_SLOPE_THRESHOLD = 0.5  # FIXED: Added missing parameter
    ULTRA_SCALP_PRICE_CHANGE_THRESHOLD = 0.5
    ULTRA_SCALP_BASE_CONFIDENCE = 0.6
    ULTRA_SCALP_RSI_DISTANCE_DIVISOR = 10
    ULTRA_SCALP_MOMENTUM_BONUS_MAX = 0.2
    ULTRA_SCALP_VOLUME_BONUS = 0.1
    ULTRA_SCALP_STOP_LOSS_PERCENT = 0.25
    ULTRA_SCALP_TAKE_PROFIT_PERCENT = 0.60
    ULTRA_SCALP_MAX_HOLD_SECONDS = 600

   
    # Fast-Scalp Strategy
    FAST_SCALP_RSI_PERIOD = 14
    FAST_SCALP_EMA_FAST = 8
    FAST_SCALP_EMA_SLOW = 21
    FAST_SCALP_RSI_BUY_THRESHOLD = 45        # RSI oversold threshold (more permissive)
    FAST_SCALP_RSI_SELL_THRESHOLD = 55       # RSI overbought threshold (more permissive)
    FAST_SCALP_MACD_FAST = 5
    FAST_SCALP_MACD_SLOW = 10
    FAST_SCALP_MACD_SIGNAL = 4
    FAST_SCALP_VOLUME_MULTIPLIER = 1.05      # Volume surge threshold
    FAST_SCALP_VOLUME_PERIOD = 10
    FAST_SCALP_VOLUME_AVERAGE_PERIOD = 10    # FIXED: Added missing parameter
    FAST_SCALP_VOLUME_SURGE_MULTIPLIER = 1.01  # Volume surge multiplier (more permissive)
    FAST_SCALP_RSI_DISTANCE_DIVISOR = 10     # RSI distance divisor
    FAST_SCALP_MACD_BONUS_MAX = 0.3          # MACD bonus maximum
    FAST_SCALP_VOLUME_BONUS = 0.1            # Volume bonus
    FAST_SCALP_BASE_CONFIDENCE = 0.4
    FAST_SCALP_VOLUME_CONFIDENCE_BONUS = 0.2
    FAST_SCALP_MIN_CONFIDENCE = 0.2
    FAST_SCALP_PROFIT_TARGET = 0.0060
    FAST_SCALP_STOP_LOSS = 0.0025
    FAST_SCALP_STOP_LOSS_PERCENT = 0.25      # 0.25% stop loss percentage
    FAST_SCALP_TAKE_PROFIT_PERCENT = 0.60    # 0.60% take profit percentage
    FAST_SCALP_MAX_HOLD_SECONDS = 900        # 15 minutes
    FAST_SCALP_RSI_OVERSOLD = 45             # FIXED: Added missing parameter
    FAST_SCALP_RSI_OVERBOUGHT = 55           # FIXED: Added missing parameter
    FAST_SCALP_PRICE_CHANGE_THRESHOLD = 0.5  # FIXED: Added missing parameter
    
    # Quick-Momentum Strategy (Golden Cross Pattern Detection)
    # GCP Pattern Detection Parameters
    QUICK_MOMENTUM_GROWTH_DETECTION_WINDOW = 20      # Window size for growth phase detection
    QUICK_MOMENTUM_PLATEAU_DETECTION_WINDOW = 15     # Window size for plateau phase detection
    QUICK_MOMENTUM_MIN_GROWTH_PERCENTAGE = 0.12      # Minimum growth/decline percentage (12%)
    QUICK_MOMENTUM_GROWTH_CONSISTENCY_THRESHOLD = 0.35  # Growth consistency requirement (35%)
    QUICK_MOMENTUM_PLATEAU_VOLATILITY_THRESHOLD = 0.7   # Plateau volatility tolerance (70%)
    QUICK_MOMENTUM_PLATEAU_DRIFT_THRESHOLD = 0.5        # Plateau drift tolerance (0.5% per period)
    QUICK_MOMENTUM_MIN_PLATEAU_DURATION = 4             # Minimum plateau duration (4 periods)
    
    # GCP Confidence Thresholds
    QUICK_MOMENTUM_MIN_PATTERN_CONFIDENCE = 0.25       # Minimum GCP pattern confidence (25%)
    QUICK_MOMENTUM_STRONG_PATTERN_CONFIDENCE = 0.5      # Strong pattern threshold (50%)
    
    # Technical Confirmation Settings
    QUICK_MOMENTUM_USE_TECHNICAL_CONFIRMATION = True    # Enable technical confirmation
    QUICK_MOMENTUM_CONFIRMATION_WEIGHT = 0.3            # Technical confirmation weight (30%)
    QUICK_MOMENTUM_GCP_WEIGHT = 0.7                     # GCP pattern weight (70%)
    
    # Risk Management Parameters
    QUICK_MOMENTUM_MIN_CONFIDENCE = 0.2                 # Overall strategy confidence threshold
    QUICK_MOMENTUM_STOP_LOSS = 0.004                    # 0.4% stop loss
    QUICK_MOMENTUM_PROFIT_TARGET = 0.008                # 0.8% take profit
    QUICK_MOMENTUM_MAX_HOLD_SECONDS = 1200              # 20 minutes max hold
    
    # TTM-Squeeze Strategy
    TTM_SQUEEZE_RSI_PERIOD = 14
    TTM_SQUEEZE_BB_PERIOD = 20
    TTM_SQUEEZE_BB_STD = 2.0
    TTM_SQUEEZE_KC_PERIOD = 20
    TTM_SQUEEZE_KC_MULTIPLIER = 1.5
    TTM_SQUEEZE_RSI_BUY_THRESHOLD = 45  # RSI oversold threshold (more permissive)
    TTM_SQUEEZE_RSI_SELL_THRESHOLD = 55  # RSI overbought threshold (more permissive)
    TTM_SQUEEZE_MIN_CONFIDENCE = 0.15  # Much lower confidence threshold
    TTM_SQUEEZE_MAX_HOLD_SECONDS = 1800  # 30 minutes
    TTM_SQUEEZE_BASE_CONFIDENCE = 0.6   # Base confidence for TTM-Squeeze
    TTM_SQUEEZE_SQUEEZE_BONUS = 0.2     # Bonus for squeeze detection
    TTM_SQUEEZE_MOMENTUM_BONUS = 0.1    # Bonus for momentum confirmation
    TTM_MAX_HOLD_SECONDS = 1800          # FIXED: Added missing parameter (alias for TTM_SQUEEZE_MAX_HOLD_SECONDS)
    
    # ==================== VOLUME ANALYSIS ====================
    
    # Volume surge thresholds (much more permissive)
    VOLUME_SURGE_THRESHOLD = 1.01  # FIXED: Much lower (was 1.2-1.5)
    VOLUME_AVERAGE_PERIOD = 7  # FIXED: Shorter period (was 10-20)
    
    # ==================== MOMENTUM ANALYSIS ====================
    
    # RSI slope thresholds (much more permissive)
    RSI_SLOPE_MIN = -1.0  # FIXED: Much more permissive (was -0.5)
    RSI_SLOPE_MAX = 1.0   # FIXED: Much more permissive (was 0.5)
    
    # Price change thresholds (much more permissive)
    PRICE_CHANGE_MIN = -1.0  # FIXED: Much more permissive (was -0.5)
    PRICE_CHANGE_MAX = 1.0   # FIXED: Much more permissive (was 0.5)
    
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
    MIN_DATA_POINTS = 20  # FIXED: Much lower (was 20)
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
