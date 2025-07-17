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
    
    # ==================== SIGNAL GENERATION ====================
    
    # Minimum confidence for any signal (0.0 to 1.0)
    MIN_CONFIDENCE = 0.2  # FIXED: Much lower than GitHub (0.4-0.5)
    
    # Maximum number of concurrent positions per symbol
    MAX_POSITIONS_PER_SYMBOL = 2
    
    # ==================== RISK MANAGEMENT ====================
    
    # Position sizing (percentage of available balance)
    POSITION_SIZE_PERCENT = 10.0  # 10% of balance per trade
    
    # Maximum total risk per trade (percentage)
    MAX_RISK_PERCENT = 2.0  # 2% max risk per trade
    
    # Stop loss and take profit defaults
    DEFAULT_STOP_LOSS_PERCENT = 0.5  # 0.5% stop loss
    DEFAULT_TAKE_PROFIT_PERCENT = 1.0  # 1.0% take profit
    
    # ====
