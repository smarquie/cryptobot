# strategies/__init__.py

from .ultra_scalp import UltraScalpStrategy
from .fast_scalp import FastScalpStrategy
from .quick_momentum import QuickMomentumStrategy
from .ttm_squeeze import TTMSqueezeStrategy

__all__ = [
    "UltraScalpStrategy",
    "FastScalpStrategy",
    "QuickMomentumStrategy",
    "TTMSqueezeStrategy"
]
