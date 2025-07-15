# strategies/signal_aggregator.py

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

    def aggregate(self, df: pd.DataFrame, symbol: str) -> dict:
        """
        Run all strategies and return best signal
        Returns 'hold' if no strategy has valid signal
        """
        signals = []
        for name, strategy in self.strategies.items():
            try:
                signal = strategy.analyze_and_signal(df, symbol)
                if signal['confidence'] >= BotConfig.ULTRA_SCALP_MIN_CONFIDENCE:
                    signal['weighted_confidence'] = signal['confidence'] * self.weights.get(name, 1.0)
                    signals.append(signal)
            except Exception as e:
                print(f"❌ Error in {name} strategy: {e}")
        
        if not signals:
            return {'action': 'hold', 'confidence': 0.0, 'reason': 'No valid signals'}
        
        # Return highest weighted confidence signal
        best_signal = max(signals, key=lambda x: x.get('weighted_confidence', x['confidence']))
        return best_signal
