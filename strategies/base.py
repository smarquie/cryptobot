# strategies/base.py

from abc import ABC
import pandas as pd
from typing import Dict, Any

class Strategy(ABC):
    def __init__(self, name: str):
        self.name = name

    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError()

    def _empty_signal(self, reason="No valid signal") -> Dict[str, Any]:
        return {
            'action': 'hold',
            'confidence': 0.0,
            'strategy': self.name,
            'entry_price': 0.0,
            'stop_loss': None,
            'take_profit': None,
            'reason': reason
        }
