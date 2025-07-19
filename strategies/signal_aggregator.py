# strategies/signal_aggregator.py
import pandas as pd
from typing import Dict, List
from .ultra_scalp import UltraScalpStrategy
from .fast_scalp import FastScalpStrategy
from .quick_momentum import QuickMomentumStrategy
from .ttm_squeeze import TTMSqueezeStrategy
from config import BotConfig

class SignalAggregator:
    def __init__(self):
        self.strategies = {
            'Ultra-Scalp': UltraScalpStrategy(),
            'Fast-Scalp': FastScalpStrategy(),
            'Quick-Momentum': QuickMomentumStrategy(),
            'TTM-Squeeze': TTMSqueezeStrategy()
        }
        self.weights = BotConfig.STRATEGY_WEIGHTS
        
        # Strategy-specific timeframes and timelines
        self.strategy_configs = {
            'Ultra-Scalp': {
                'timeframe': '1m',
                'lookback': 10,
                'max_hold_time': 600,  # 10 minutes
                'target_hold': '10 minutes',
                'description': 'Ultra-fast scalping with 1-minute timeframe'
            },
            'Fast-Scalp': {
                'timeframe': '5m',
                'lookback': 20,
                'max_hold_time': 1800,  # 30 minutes
                'target_hold': '30 minutes',
                'description': 'Fast scalping with 5-minute timeframe'
            },
            'Quick-Momentum': {
                'timeframe': '15m',
                'lookback': 40,
                'max_hold_time': 3600,  # 1 hour
                'target_hold': '1 hour',
                'description': 'Momentum trading with 15-minute timeframe'
            },
            'TTM-Squeeze': {
                'timeframe': '1h',
                'lookback': 24,
                'max_hold_time': 14400,  # 4 hours
                'target_hold': '4 hours',
                'description': 'Squeeze breakout with 1-hour timeframe'
            }
        }

    def aggregate(self, market_data: Dict, symbol: str) -> List[Dict]:
        """
        Run ALL strategies and return ALL valid signals
        Returns list of signals that can be executed simultaneously
        """
        all_signals = []
        
        for strategy_name, strategy in self.strategies.items():
            try:
                # Get strategy-specific timeframe
                config = self.strategy_configs[strategy_name]
                timeframe = config['timeframe']
                lookback = config['lookback']
                
                # Get data for this strategy's timeframe
                df = market_data.get(f"{symbol}_{timeframe}")
                if df is None or df.empty:
                    continue
                
                # Run strategy analysis
                signal = strategy.analyze_and_signal(df, symbol)
                
                # Add strategy-specific timeline information
                signal.update({
                    'timeframe': timeframe,
                    'lookback_periods': lookback,
                    'max_hold_time': config['max_hold_time'],
                    'target_hold': config['target_hold'],
                    'description': config['description'],
                    'weighted_confidence': signal['confidence'] * self.weights.get(strategy_name, 1.0)
                })
                
                # Check if signal meets minimum confidence
                min_confidence_key = f"{strategy_name.upper().replace('-', '_')}_MIN_CONFIDENCE"
                min_confidence = getattr(BotConfig, min_confidence_key, BotConfig.MIN_CONFIDENCE)
                
                if signal['confidence'] >= min_confidence:
                    all_signals.append(signal)
                    
            except Exception as e:
                print(f"❌ Error in {strategy_name} strategy: {e}")
        
        return all_signals

    def get_strategy_timeline_info(self, strategy_name: str) -> Dict:
        """Get timeline information for a specific strategy"""
        return self.strategy_configs.get(strategy_name, {})

    def get_all_timelines(self) -> Dict:
        """Get timeline information for all strategies"""
        return self.strategy_configs
