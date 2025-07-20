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
        # FIXED: Don't access weights during __init__ to avoid import issues
        self._weights = None
        
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
                # Get strategy-specific timeframe
                config = self.strategy_configs[strategy_name]
                timeframe = config['timeframe']
                lookback = config['lookback']
                
                # Get data for this strategy's timeframe
                df = market_data.get(f"{symbol}_{timeframe}")
                if df is None or df.empty:
                    print(f"⚠️ No data for {symbol}_{timeframe}")
                    continue
                
                # Ensure DataFrame has required columns
                required_columns = ['open', 'high', 'low', 'close', 'volume']
                if not all(col in df.columns for col in required_columns):
                    print(f"⚠️ Missing required columns for {symbol}_{timeframe}")
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
                    print(f"✅ {strategy_name} generated valid signal: {signal['action']} (conf: {signal['confidence']:.3f})")
                else:
                    print(f"📊 {strategy_name} signal below threshold: {signal['confidence']:.3f} < {min_confidence}")
                    
            except Exception as e:
                print(f"❌ Error in {strategy_name} strategy: {e}")
                import traceback
                traceback.print_exc()
        
        # NEW: Apply 3-strategy agreement logic
        return self._apply_agreement_logic(all_signals, symbol)

    def _apply_agreement_logic(self, signals: List[Dict], symbol: str) -> List[Dict]:
        """
        Apply 2-strategy agreement logic (changed from 3+):
        - Only return signals when 2+ strategies agree on direction
        - Group by action (buy/sell)
        - Return highest confidence signals for agreed direction
        """
        if len(signals) < 2:
            print(f"📊 {symbol}: Only {len(signals)} valid signals (need 2+ for agreement)")
            return []
        
        # Group signals by action
        buy_signals = [s for s in signals if s['action'] == 'buy']
        sell_signals = [s for s in signals if s['action'] == 'sell']
        
        print(f"📊 {symbol}: {len(buy_signals)} buy signals, {len(sell_signals)} sell signals")
        
        # Check for 2+ strategy agreement (changed from 3+)
        if len(buy_signals) >= 2:
            print(f"✅ {symbol}: 2+ strategies agree on BUY direction")
            # Return top 2 buy signals by confidence
            return sorted(buy_signals, key=lambda x: x['confidence'], reverse=True)[:2]
        elif len(sell_signals) >= 2:
            print(f"✅ {symbol}: 2+ strategies agree on SELL direction")
            # Return top 2 sell signals by confidence
            return sorted(sell_signals, key=lambda x: x['confidence'], reverse=True)[:2]
        else:
            print(f"📊 {symbol}: No 2-strategy agreement (buy: {len(buy_signals)}, sell: {len(sell_signals)})")
            return []

    def get_strategy_timeline_info(self, strategy_name: str) -> Dict:
        """Get timeline information for a specific strategy"""
        return self.strategy_configs.get(strategy_name, {})

    def get_all_timelines(self) -> Dict:
        """Get timeline information for all strategies"""
        return self.strategy_configs
