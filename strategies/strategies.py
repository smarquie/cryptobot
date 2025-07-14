# strategies/strategies.py

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any
from config import BotConfig
from utils.ta import TechnicalAnalysis as TA

class Strategy(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Return signal dict with action, confidence, stop loss, take profit, reason"""
        pass

    def _empty_signal(self, reason: str = "No valid signal") -> Dict[str, Any]:
        return {
            'action': 'hold',
            'confidence': 0.0,
            'strategy': self.name,
            'entry_price': 0.0,
            'stop_loss': 0.0,
            'take_profit': 0.0,
            'reason': reason,
            'max_hold_time': 600,
            'target_hold': '10 minutes'
        }
