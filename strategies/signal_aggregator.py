#!/usr/bin/env python3
"""
SIGNAL AGGREGATOR - FIXED WITH POSITION CHECKING
Prevents signals for strategies that already have positions
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
        
        # FIXED: Add portfolio reference for position checking
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
                'max_hold_time': BotConfig.MOMENTUM_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.MOMENTUM_MAX_HOLD_SECONDS//60} minutes',
                'description': 'Momentum trading with 1-minute data'
            },
            'TTM-Squeeze': {
                'timeframe': '1m',
                'lookback': 20,  # Needs 20 minutes of 1-minute data
                'max_hold_time': BotConfig.TTM_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.TTM_MAX_HOLD_SECONDS//60} minutes',
                'description': 'Squeeze breakout with 1-minute data'
            }
        }
    
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
        Run ALL strategies and return signals only when 2+ strategies agree on direction
        Returns list of signals that meet the agreement threshold
        """
        all_signals = []
        
        for strategy_name, strategy in self.strategies.items():
            try:
                # All strategies use 1-minute data
                config = self.strategy_configs[strategy_name]
                lookback = config['lookback']
                
                # Get 1-minute data for this strategy
                df = market_data.get(f"{symbol}_1m")
                if df is None or df.empty:
                    print(f"⚠️ No 1m data for {symbol}")
                    continue
                
                # Use only the required number of recent data points
                if len(df) >= lookback:
                    df = df.tail(lookback)
                else:
                    print(f"⚠️ Insufficient 1m data for {strategy_name}: {len(df)} < {lookback}")
                    continue
                
                # Ensure DataFrame has required columns
                required_columns = ['open', 'high', 'low', 'close', 'volume']
                if not all(col in df.columns for col in required_columns):
                    print(f"⚠️ Missing required columns for {symbol}_1m")
                    continue
                
                # FIXED: Check if this strategy already has a position for this symbol
                if self.portfolio and self.portfolio.has_position_for_strategy(symbol, strategy_name):
                    print(f"📊 {symbol} ({strategy_name}): Strategy already has position - skipping")
                    continue
                
                # Run strategy analysis
                signal = strategy.analyze_and_signal(df, symbol)
                
                # Validate signal is a dictionary
                if not isinstance(signal, dict):
                    print(f"⚠️ {strategy_name} returned non-dict signal: {type(signal)}")
                    continue
                
                # Ensure signal has required fields
                required_signal_fields = ['action', 'confidence', 'strategy', 'reason']
                if not all(field in signal for field in required_signal_fields):
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
                
                # FIXED: Don't filter by confidence threshold here - let individual strategies handle it
                # Only add signals that have valid actions (not 'hold')
                if signal['action'] != 'hold':
                    all_signals.append(signal)
                    print(f"✅ {strategy_name} generated valid signal: {signal['action']} (conf: {signal['confidence']:.3f})")
                else:
                    print(f"📊 {strategy_name}: No signal (hold)")
                    
            except Exception as e:
                print(f"❌ Error in {strategy_name} strategy: {e}")
                import traceback
                traceback.print_exc()
        
        # NEW: Apply 3-strategy agreement logic
        return self._apply_agreement_logic(all_signals, symbol)

    def _apply_agreement_logic(self, signals: List[Dict], symbol: str) -> List[Dict]:
        """
        Apply 1-strategy agreement logic (changed from 2+):
        - Return signals when 1+ strategies generate signals
        - Group by action (buy/sell)
        - Return highest confidence signals for each direction
        """
        if len(signals) < 1:
            print(f"📊 {symbol}: Only {len(signals)} valid signals (need 1+ for agreement)")
            return []
        
        # Group signals by action
        buy_signals = [s for s in signals if s['action'] == 'buy']
        sell_signals = [s for s in signals if s['action'] == 'sell']
        
        print(f"📊 {symbol}: {len(buy_signals)} buy signals, {len(sell_signals)} sell signals")
        
        # Check for 1+ strategy agreement (changed from 2+)
        if len(buy_signals) >= 1:
            print(f"✅ {symbol}: 1+ strategies agree on BUY direction")
            # Return top buy signal by confidence
            return sorted(buy_signals, key=lambda x: x['confidence'], reverse=True)[:1]
        elif len(sell_signals) >= 1:
            print(f"✅ {symbol}: 1+ strategies agree on SELL direction")
            # Return top sell signal by confidence
            return sorted(sell_signals, key=lambda x: x['confidence'], reverse=True)[:1]
        else:
            print(f"📊 {symbol}: No 1-strategy agreement (buy: {len(buy_signals)}, sell: {len(sell_signals)})")
            return []

    def get_strategy_timeline_info(self, strategy_name: str) -> Dict:
        """Get timeline information for a specific strategy"""
        return self.strategy_configs.get(strategy_name, {})

    def get_all_timelines(self) -> Dict:
        """Get timeline information for all strategies"""
        return self.strategy_configs


    def get_all_timelines(self) -> Dict:
        """Get timeline information for all strategies"""
        return self.strategy_configs
