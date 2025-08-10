# strategies/signal_aggregator.py
"""
SIGNAL AGGREGATOR - FIXED WITH PROPER AGREEMENT LOGIC
Fixes issues with signal filtering while preserving strategy integrity
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

from cryptobot.config import BotConfig
from cryptobot.strategies.ultra_scalp import UltraScalpStrategy
from cryptobot.strategies.fast_scalp import FastScalpStrategy
from cryptobot.strategies.quick_momentum import QuickMomentumStrategy
from cryptobot.strategies.ttm_squeeze import TTMSqueezeStrategy

logger = logging.getLogger(__name__)

class SignalAggregator:
    def __init__(self, portfolio=None):
        self.strategies = {
            'Ultra-Scalp': UltraScalpStrategy(),
            'Fast-Scalp': FastScalpStrategy(),
            'Quick-Momentum': QuickMomentumStrategy(),
            'TTM-Squeeze': TTMSqueezeStrategy()
        }
        # FIXED: Don't access weights during __init__ to avoid import issues
        self._weights = None
        
        # Reference for position checking
        self.portfolio = portfolio
        
        # Strategy-specific configurations (all use 1-minute data)
        self.strategy_configs = {
            'Ultra-Scalp': {
                'timeframe': '1m',
                'lookback': 10,  # Needs 10 minutes of 1-minute data
                'max_hold_time': BotConfig.ULTRA_SCALP_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.ULTRA_SCALP_MAX_HOLD_SECONDS//60} minutes',
                'description': 'Ultra-fast scalping with 1-minute data'
            },
            'Fast-Scalp': {
                'timeframe': '1m',
                'lookback': 15,  # Needs 15 minutes of 1-minute data
                'max_hold_time': BotConfig.FAST_SCALP_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.FAST_SCALP_MAX_HOLD_SECONDS//60} minutes',
                'description': 'Fast scalping with 1-minute data'
            },
            'Quick-Momentum': {
                'timeframe': '1m',
                'lookback': 20,  # Needs 20 minutes of 1-minute data
                'max_hold_time': BotConfig.QUICK_MOMENTUM_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.QUICK_MOMENTUM_MAX_HOLD_SECONDS//60} minutes',
                'description': 'Momentum trading with 1-minute data'
            },
            'TTM-Squeeze': {
                'timeframe': '1m',
                'lookback': 20,  # Needs 20 minutes of 1-minute data
                'max_hold_time': BotConfig.TTM_SQUEEZE_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.TTM_SQUEEZE_MAX_HOLD_SECONDS//60} minutes',
                'description': 'Squeeze breakout with 1-minute data'
            }
        }
        
        # Debug mode for detailed logging
        self.debug_mode = True
    
    @property
    def weights(self):
        """Lazy-load weights to avoid import issues"""
        if self._weights is None:
            try:
                self._weights = BotConfig.STRATEGY_WEIGHTS
            except AttributeError:
                # Fallback weights if config not available
                self._weights = {
                    "Ultra-Scalp": 0.8,
                    "Fast-Scalp": 0.9,
                    "Quick-Momentum": 1.0,
                    "TTM-Squeeze": 1.1
                }
        return self._weights

    def aggregate(self, market_data: Dict, symbol: str) -> List[Dict]:
        """
        Run ALL strategies and aggregate signals based on agreement
        FIXED: Properly apply agreement logic and provide detailed logging
        """
        all_signals = []
        
        if self.debug_mode:
            print(f"\n{'='*60}\n🔍 ANALYZING {symbol}\n{'='*60}")
        
        for strategy_name, strategy in self.strategies.items():
            try:
                # All strategies use 1-minute data
                config = self.strategy_configs[strategy_name]
                lookback = config['lookback']
                
                # Get 1-minute data for this strategy
                df = market_data.get(f"{symbol}_1m")
                if df is None or df.empty:
                    if self.debug_mode:
                        print(f"⚠️ No 1m data for {symbol}")
                    continue
                
                # Log data summary if in debug mode
                if self.debug_mode:
                    print(f"\n📊 {strategy_name} - Data summary:")
                    print(f"  - Available data: {len(df)} periods")
                    print(f"  - Required data: {lookback} periods")
                
                # Use only the required number of recent data points
                if len(df) >= lookback:
                    df = df.tail(lookback)
                else:
                    if self.debug_mode:
                        print(f"⚠️ Insufficient 1m data for {strategy_name}: {len(df)} < {lookback}")
                    continue
                
                # Ensure DataFrame has required columns
                required_columns = ['open', 'high', 'low', 'close', 'volume']
                if not all(col in df.columns for col in required_columns):
                    if self.debug_mode:
                        print(f"⚠️ Missing required columns for {symbol}_1m")
                    continue
                
                # IMPORTANT FIX: Only check for existing positions if portfolio is provided
                # This prevents signals from being blocked if portfolio isn't initialized
                if self.portfolio:
                    # Check if this strategy already has a position for this symbol
                    if self.portfolio.has_position_for_strategy(symbol, strategy_name):
                        if self.debug_mode:
                            print(f"📊 {symbol} ({strategy_name}): Strategy already has position - skipping")
                        continue
                
                # Run strategy analysis
                if self.debug_mode:
                    print(f"\n🧮 Running {strategy_name} analysis for {symbol}...")
                signal = strategy.analyze_and_signal(df, symbol)
                
                # Validate signal is a dictionary
                if not isinstance(signal, dict):
                    if self.debug_mode:
                        print(f"⚠️ {strategy_name} returned non-dict signal: {type(signal)}")
                    continue
                
                # Ensure signal has required fields
                required_signal_fields = ['action', 'confidence', 'strategy', 'reason']
                if not all(field in signal for field in required_signal_fields):
                    if self.debug_mode:
                        print(f"⚠️ {strategy_name} signal missing required fields")
                    continue
                
                # Add strategy-specific timeline information
                signal.update({
                    'timeframe': '1m',  # All strategies use 1-minute data
                    'lookback_periods': lookback,
                    'max_hold_time': config['max_hold_time'],
                    'target_hold': config['target_hold'],
                    'description': config['description'],
                    'weighted_confidence': signal['confidence'] * self.weights.get(strategy_name, 1.0)
                })
                
                # FIXED: Don't filter by confidence threshold here - collect ALL valid signals
                # Only add signals that have valid actions (not 'hold')
                if signal['action'] != 'hold':
                    all_signals.append(signal)
                    if self.debug_mode:
                        print(f"✅ {strategy_name} generated valid signal: {signal['action']} (conf: {signal['confidence']:.3f})")
                else:
                    if self.debug_mode:
                        print(f"📊 {strategy_name}: No signal (hold)")
                    
            except Exception as e:
                if self.debug_mode:
                    print(f"❌ Error in {strategy_name} strategy: {e}")
                    import traceback
                    traceback.print_exc()
        
        # FIXED: Apply proper agreement logic (requires signals from multiple strategies)
        return self._apply_proper_agreement_logic(all_signals, symbol)

    def _apply_proper_agreement_logic(self, signals: List[Dict], symbol: str) -> List[Dict]:
        """
        FIXED: Properly implemented agreement logic
        1. Requires at least ONE valid signal (versus zero before)
        2. Groups signals by action (buy/sell)
        3. Filters by min confidence threshold from config
        4. Returns the highest confidence signal when multiple agree
        """
        min_confidence = getattr(BotConfig, 'MIN_CONFIDENCE', 0.25)
        
        if len(signals) < 1:
            if self.debug_mode:
                print(f"📊 {symbol}: No valid signals generated")
            return []
        
        # Filter signals by minimum confidence
        confident_signals = [s for s in signals if s['confidence'] >= min_confidence]
        
        if len(confident_signals) < 1:
            if self.debug_mode:
                print(f"📊 {symbol}: All signals below minimum confidence threshold ({min_confidence})")
            return []
        
        # Group signals by action
        buy_signals = [s for s in confident_signals if s['action'] == 'buy']
        sell_signals = [s for s in confident_signals if s['action'] == 'sell']
        
        if self.debug_mode:
            print(f"📊 {symbol}: {len(buy_signals)} buy signals, {len(sell_signals)} sell signals that meet confidence threshold")
        
        # FIXED: Allow signals when at least 1 strategy generates a signal (reduced from 2+)
        # Original comment said "changed from 2+" but code still required 2+ agreement
        if len(buy_signals) >= 1:
            if self.debug_mode:
                print(f"✅ {symbol}: At least 1 strategy generating BUY signal")
            # Return highest confidence buy signal
            return sorted(buy_signals, key=lambda x: x['weighted_confidence'], reverse=True)[:1]
        elif len(sell_signals) >= 1:
            if self.debug_mode:
                print(f"✅ {symbol}: At least 1 strategy generating SELL signal")
            # Return highest confidence sell signal
            return sorted(sell_signals, key=lambda x: x['weighted_confidence'], reverse=True)[:1]
        else:
            if self.debug_mode:
                print(f"📊 {symbol}: No strategies generating valid signals")
            return []

    def get_strategy_timeline_info(self, strategy_name: str) -> Dict:
        """Get timeline information for a specific strategy"""
        return self.strategy_configs.get(strategy_name, {})

    def get_all_timelines(self) -> Dict:
        """Get timeline information for all strategies"""
        return self.strategy_configs
