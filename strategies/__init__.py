# strategies/__init__.py

from .signal_aggregator import SignalAggregator
from .ultra_scalp import UltraScalpStrategy
from .fast_scalp import FastScalpStrategy
from .quick_momentum import QuickMomentumStrategy
from .ttm_squeeze import TTMSqueezeStrategy

__all__ = [
    "SignalAggregator",
    "UltraScalpStrategy",
    "FastScalpStrategy",
    "QuickMomentumStrategy",
    "TTMSqueezeStrategy"
]
