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
