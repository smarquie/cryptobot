#!/usr/bin/env python3
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
    
    # Cycle timing
    CYCLE_INTERVAL = 15  # seconds between trading cycles
    
    # Data validation (KEEP THIS - necessary for indicators)
    MIN_DATA_MINUTES = 20  # Extended from 13 to 20 for TTM Squeeze
    DATA_VALIDATION_ENABLED = True  # KEEP ENABLED - necessary for indicators
    
    # ==================== ULTRA-SCALP STRATEGY PARAMETERS ====================
    
    # RSI Thresholds - FIXED: Much more permissive
    ULTRA_SCALP_RSI_BUY_THRESHOLD = 40      # FIXED: From 30 to 40
    ULTRA_SCALP_RSI_SELL_THRESHOLD = 60     # FIXED: From 70 to 60
    
    # Price vs SMA conditions
    ULTRA_SCALP_SMA_BUY_MULTIPLIER = 0.998   # Buy when price < SMA * this
    ULTRA_SCALP_SMA_SELL_MULTIPLIER = 1.002  # Sell when price > SMA * this
    
    # Price change filters (1-minute momentum) - IMPROVED
    ULTRA_SCALP_MAX_NEGATIVE_CHANGE = -0.50  # Increased from -0.25 to -0.50%
    ULTRA_SCALP_MAX_POSITIVE_CHANGE = 0.50   # Increased from 0.25 to 0.50%
    
    # Profit and stop loss targets (IMPROVED)
    ULTRA_SCALP_PROFIT_TARGET = 0.0050       # Increased from 0.40% to 0.50%
    ULTRA_SCALP_STOP_LOSS = 0.0025           # Increased from 0.20% to 0.25%
    
    # Hold time limits
    ULTRA_SCALP_MAX_HOLD_SECONDS = 600       # 10 minutes max hold
    
    # Confidence calculation - FIXED: Much more permissive
    ULTRA_SCALP_BASE_CONFIDENCE = 0.5        # FIXED: Increased from 0.4
    ULTRA_SCALP_RSI_CONFIDENCE_FACTOR = 20   # RSI distance factor for confidence
    ULTRA_SCALP_MIN_CONFIDENCE = 0.2         # FIXED: Much lower from 0.4
    
    # Technical indicator periods
    ULTRA_SCALP_RSI_PERIOD = 7               # RSI calculation period
    ULTRA_SCALP_SMA_PERIOD = 5               # SMA calculation period
    
    # ==================== FAST-SCALP STRATEGY PARAMETERS ====================
    
    # RSI Thresholds - FIXED: Much more permissive
    FAST_SCALP_RSI_BUY_THRESHOLD = 40        # FIXED: From 30 to 40
    FAST_SCALP_RSI_SELL_THRESHOLD = 60       # FIXED: From 70 to 60
    
    # MACD Parameters
    FAST_SCALP_MACD_FAST = 5                 # MACD fast EMA period
    FAST_SCALP_MACD_SLOW = 10                # MACD slow EMA period
    FAST_SCALP_MACD_SIGNAL = 4               # MACD signal line period
    
    # Volume confirmation
    FAST_SCALP_VOLUME_MULTIPLIER = 1.10      # Volume must be > average * this
    FAST_SCALP_VOLUME_PERIOD = 10            # Volume average period
    
    # Profit and stop loss targets (IMPROVED)
    FAST_SCALP_PROFIT_TARGET = 0.0050        # Increased from 0.40% to 0.50%
    FAST_SCALP_STOP_LOSS = 0.0025             # Increased from 0.20% to 0.25%
    
    # Hold time limits
    FAST_SCALP_MAX_HOLD_SECONDS = 900        # 15 minutes max hold
    
    # Confidence calculation - FIXED: Much more permissive
    FAST_SCALP_BASE_CONFIDENCE = 0.6         # Base confidence level
    FAST_SCALP_VOLUME_CONFIDENCE_BONUS = 0.2 # Bonus for high volume
    FAST_SCALP_MIN_CONFIDENCE = 0.2          # FIXED: Much lower from 0.4
    
    # ==================== QUICK-MOMENTUM STRATEGY PARAMETERS ====================
    
    # RSI Thresholds (FIXED - was inverted)
    MOMENTUM_RSI_BUY_THRESHOLD = 35           # Buy when RSI rising from low levels
    MOMENTUM_RSI_SELL_THRESHOLD = 65          # Sell when RSI falling from high levels
    
    # Moving average periods
    MOMENTUM_FAST_MA_PERIOD = 3               # Fast moving average
    MOMENTUM_SLOW_MA_PERIOD = 8               # Slow moving average
    
    # Momentum confirmation (IMPROVED)
    MOMENTUM_MIN_PRICE_CHANGE = 0.02          # Reduced from 0.05 to 0.02% (more realistic)
    MOMENTUM_TREND_PERIODS = 3                # Periods to confirm trend
    
    # Profit and stop loss targets (IMPROVED)
    MOMENTUM_PROFIT_TARGET = 0.0060            # Increased to 0.60% profit target
    MOMENTUM_STOP_LOSS = 0.003                # Increased to 0.30% stop loss
    
    # Hold time limits
    MOMENTUM_MAX_HOLD_SECONDS = 1800          # 30 minutes max hold
    
    # Confidence calculation - FIXED: Much more permissive
    MOMENTUM_BASE_CONFIDENCE = 0.5            # Base confidence level
    MOMENTUM_TREND_CONFIDENCE_BONUS = 0.3     # Bonus for strong trend
    MOMENTUM_MIN_CONFIDENCE = 0.2             # FIXED: Much lower from 0.4
    
    # ==================== TTM SQUEEZE + CVD STRATEGY PARAMETERS ====================
    
    # TTM Squeeze Parameters
    TTM_BB_PERIOD = 20                        # Bollinger Bands period
    TTM_BB_STDDEV = 2.0                       # Bollinger Bands standard deviation
    TTM_KC_PERIOD = 20                        # Keltner Channel period
    TTM_KC_ATR_MULTIPLIER = 1.5               # Keltner Channel ATR multiplier
    TTM_MOMENTUM_PERIOD = 20                  # Momentum calculation period
    
    # CVD Parameters
    TTM_CVD_LOOKBACK = 20                     # CVD calculation lookback
    TTM_CVD_DIVERGENCE_THRESHOLD = 0.7        # CVD divergence threshold
    
    # Entry Conditions - FIXED: Much more permissive
    TTM_MIN_SQUEEZE_PERIODS = 2               # FIXED: Lower from 3 to 2
    TTM_MOMENTUM_THRESHOLD = 0.5              # Minimum momentum for entry
    TTM_CVD_MOMENTUM_THRESHOLD = 0.3          # Minimum CVD momentum for entry
    
    # Profit and stop loss targets (IMPROVED)
    TTM_PROFIT_TARGET = 0.003                 # Increased from 0.20% to 0.30%
    TTM_STOP_LOSS = 0.002                     # Increased from 0.15% to 0.20%
    
    # Hold time limits
    TTM_MAX_HOLD_SECONDS = 1200               # 20 minutes max hold
    
    # Confidence calculation - FIXED: Much more permissive
    TTM_BASE_CONFIDENCE = 0.6                 # Base confidence level
    TTM_SQUEEZE_CONFIDENCE_BONUS = 0.2        # Bonus for strong squeeze
    TTM_CVD_CONFIDENCE_BONUS = 0.2            # Bonus for CVD confirmation
    TTM_MIN_CONFIDENCE = 0.2                  # FIXED: Much lower from 0.5
    
    # ==================== POSITION SIZING PARAMETERS ====================
    
    # Position sizing mode: "conservative", "moderate", "aggressive"
    POSITION_SIZE_MODE = "aggressive"
    
    # Risk per trade (as fraction of portfolio)
    CONSERVATIVE_RISK_PER_TRADE = 0.10        # 10%
    MODERATE_RISK_PER_TRADE = 0.15            # 15%
    AGGRESSIVE_RISK_PER_TRADE = 0.20          # 20%
    
    # Maximum position size (as fraction of portfolio)
    CONSERVATIVE_MAX_POSITION = 0.20          # 20%
    MODERATE_MAX_POSITION = 0.25              # 25%
    AGGRESSIVE_MAX_POSITION = 0.30            # 30%
    
    # Maximum total exposure (as fraction of portfolio)
    CONSERVATIVE_MAX_EXPOSURE = 0.50          # 50%
    MODERATE_MAX_EXPOSURE = 0.70              # 70%
    AGGRESSIVE_MAX_EXPOSURE = 0.90            # 90%
    
    # ==================== API CREDENTIALS ====================
    
    # Hyperliquid API
    HYPERLIQUID_PRIVATE_KEY = "d9aa9fed2d6cc39cbd95dc0f40f0a7ba54d2de4b92c27171fdd70901946d1839"
    HYPERLIQUID_ACCOUNT_ADDRESS = "0x05b8D093Ab5772b46B95B07A9770085cEC1358b2"
    USE_TESTNET = False
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = "8038082627:AAGDuc5rZoGzYh_hsl6q2OH6tCeobGfrLFU"
    TELEGRAM_CHAT_ID = "7916999150"
    TELEGRAM_ENABLED = True
    
    # ==================== HELPER METHODS ====================
    
    @classmethod
    def get_position_sizing_config(cls):
        """Get position sizing configuration based on mode"""
        if cls.POSITION_SIZE_MODE == "conservative":
            return {
                'risk_per_trade': cls.CONSERVATIVE_RISK_PER_TRADE,
                'max_position_pct': cls.CONSERVATIVE_MAX_POSITION,
                'max_total_exposure': cls.CONSERVATIVE_MAX_EXPOSURE
            }
        elif cls.POSITION_SIZE_MODE == "moderate":
            return {
                'risk_per_trade': cls.MODERATE_RISK_PER_TRADE,
                'max_position_pct': cls.MODERATE_MAX_POSITION,
                'max_total_exposure': cls.MODERATE_MAX_EXPOSURE
            }
        else:  # aggressive
            return {
                'risk_per_trade': cls.AGGRESSIVE_RISK_PER_TRADE,
                'max_position_pct': cls.AGGRESSIVE_MAX_POSITION,
                'max_total_exposure': cls.AGGRESSIVE_MAX_EXPOSURE
            }
    
    @classmethod
    def print_current_settings(cls):
        """Print current trading parameters"""
        print("\n🎯 CURRENT TRADING PARAMETERS - FIXED VERSION")
        print("=" * 50)
        
        print(f"\n�� SYMBOLS: {cls.TRADING_SYMBOLS}")
        print(f"�� BALANCE: ${cls.PAPER_INITIAL_BALANCE:,}")
        print(f"⏱️ CYCLE: {cls.CYCLE_INTERVAL}s")
        print(f"📊 DATA VALIDATION: {'DISABLED' if not cls.DATA_VALIDATION_ENABLED else f'{cls.MIN_DATA_MINUTES} minutes'}")
        
        print(f"\n⚡ ULTRA-SCALP (FIXED):")
        print(f"   RSI: Buy<{cls.ULTRA_SCALP_RSI_BUY_THRESHOLD}, Sell>{cls.ULTRA_SCALP_RSI_SELL_THRESHOLD}")
        print(f"   Min Confidence: {cls.ULTRA_SCALP_MIN_CONFIDENCE}")
        print(f"   Profit: {cls.ULTRA_SCALP_PROFIT_TARGET*100:.2f}%, Stop: {cls.ULTRA_SCALP_STOP_LOSS*100:.2f}%")
        
        print(f"\n🔥 FAST-SCALP (FIXED):")
        print(f"   RSI: Buy<{cls.FAST_SCALP_RSI_BUY_THRESHOLD}, Sell>{cls.FAST_SCALP_RSI_SELL_THRESHOLD}")
        print(f"   Min Confidence: {cls.FAST_SCALP_MIN_CONFIDENCE}")
        print(f"   Volume Multiplier: {cls.FAST_SCALP_VOLUME_MULTIPLIER}")
        
        print(f"\n📈 MOMENTUM (FIXED):")
        print(f"   RSI: Buy>{cls.MOMENTUM_RSI_BUY_THRESHOLD}, Sell<{cls.MOMENTUM_RSI_SELL_THRESHOLD}")
        print(f"   Min Confidence: {cls.MOMENTUM_MIN_CONFIDENCE}")
        print(f"   Min Price Change: {cls.MOMENTUM_MIN_PRICE_CHANGE}%")
        
        print(f"\n�� TTM SQUEEZE (FIXED):")
        print(f"   Min Squeeze Periods: {cls.TTM_MIN_SQUEEZE_PERIODS}")
        print(f"   Min Confidence: {cls.TTM_MIN_CONFIDENCE}")
        print(f"   Momentum Threshold: {cls.TTM_MOMENTUM_THRESHOLD}")
        
        sizing = cls.get_position_sizing_config()
        print(f"\n�� POSITION SIZING ({cls.POSITION_SIZE_MODE.upper()}):")
        print(f"   Risk/trade: {sizing['risk_per_trade']*100:.1f}%")
        print(f"   Max position: {sizing['max_position_pct']*100:.1f}%")
        print(f"   Max exposure: {sizing['max_total_exposure']*100:.1f}%")
        
        print(f"\n🔧 MAJOR FIXES APPLIED:")
        print(f"   ✅ RSI thresholds: 30/70 → 40/60")
        print(f"   ✅ Confidence minimums: 0.4-0.5 → 0.2")
        print(f"   ✅ Data collection: 20 minutes (preserved)")
        print(f"   ✅ Much more permissive entry conditions")
        print(f"   ✅ Better risk-reward ratios")

# Export the BotConfig class
__all__ = ['BotConfig']
