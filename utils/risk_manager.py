"""
Dynamic Risk Management for Stop Loss and Take Profit
Allows real-time adjustment of risk parameters while bot runs
"""

import logging
from typing import Dict, Any
from cryptobot.config import BotConfig

logger = logging.getLogger(__name__)

class DynamicRiskManager:
    """
    Manages dynamic stop loss and take profit levels
    Can be adjusted while the bot runs
    """
    
    def __init__(self):
        # Initialize with config values
        self.dynamic_stop_loss_percent = BotConfig.DYNAMIC_STOP_LOSS_PERCENT
        self.dynamic_take_profit_percent = BotConfig.DYNAMIC_TAKE_PROFIT_PERCENT
        
        # Strategy-specific dynamic settings
        self.strategy_sl_tp = {
            "Ultra-Scalp": {
                "stop_loss": BotConfig.DYNAMIC_ULTRA_SCALP_SL,
                "take_profit": BotConfig.DYNAMIC_ULTRA_SCALP_TP
            },
            "Fast-Scalp": {
                "stop_loss": BotConfig.DYNAMIC_FAST_SCALP_SL,
                "take_profit": BotConfig.DYNAMIC_FAST_SCALP_TP
            },
            "Quick-Momentum": {
                "stop_loss": BotConfig.DYNAMIC_QUICK_MOMENTUM_SL,
                "take_profit": BotConfig.DYNAMIC_QUICK_MOMENTUM_TP
            },
            "TTM-Squeeze": {
                "stop_loss": BotConfig.DYNAMIC_TTM_SQUEEZE_SL,
                "take_profit": BotConfig.DYNAMIC_TTM_SQUEEZE_TP
            }
        }
        
        logger.info("🛡️ Dynamic Risk Manager initialized")
        self._log_current_settings()
    
    def _log_current_settings(self):
        """Log current risk settings"""
        logger.info("📊 Current Risk Settings:")
        logger.info(f"   Global SL: {self.dynamic_stop_loss_percent}%")
        logger.info(f"   Global TP: {self.dynamic_take_profit_percent}%")
        for strategy, settings in self.strategy_sl_tp.items():
            logger.info(f"   {strategy}: SL {settings['stop_loss']}%, TP {settings['take_profit']}%")
    
    def update_global_risk(self, 
                          stop_loss_percent: float = None,
                          take_profit_percent: float = None):
        """
        Update global stop loss and take profit percentages
        """
        if stop_loss_percent is not None:
            self.dynamic_stop_loss_percent = stop_loss_percent
            logger.info(f"🛡️ Updated global stop loss: {stop_loss_percent}%")
        
        if take_profit_percent is not None:
            self.dynamic_take_profit_percent = take_profit_percent
            logger.info(f"💰 Updated global take profit: {take_profit_percent}%")
        
        logger.info("✅ Global risk settings updated")
    
    def update_strategy_risk(self, 
                           strategy_name: str,
                           stop_loss_percent: float = None,
                           take_profit_percent: float = None):
        """
        Update risk settings for a specific strategy
        """
        if strategy_name not in self.strategy_sl_tp:
            logger.error(f"❌ Strategy '{strategy_name}' not found")
            return False
        
        if stop_loss_percent is not None:
            self.strategy_sl_tp[strategy_name]["stop_loss"] = stop_loss_percent
            logger.info(f"🛡️ Updated {strategy_name} stop loss: {stop_loss_percent}%")
        
        if take_profit_percent is not None:
            self.strategy_sl_tp[strategy_name]["take_profit"] = take_profit_percent
            logger.info(f"💰 Updated {strategy_name} take profit: {take_profit_percent}%")
        
        logger.info(f"✅ {strategy_name} risk settings updated")
        return True
    
    def update_all_strategies_risk(self,
                                 stop_loss_percent: float = None,
                                 take_profit_percent: float = None):
        """
        Update risk settings for all strategies at once
        """
        for strategy_name in self.strategy_sl_tp.keys():
            self.update_strategy_risk(strategy_name, stop_loss_percent, take_profit_percent)
        
        logger.info("✅ All strategy risk settings updated")
    
    def get_risk_settings(self, strategy_name: str = None) -> Dict[str, Any]:
        """
        Get current risk settings
        """
        if strategy_name:
            if strategy_name not in self.strategy_sl_tp:
                return {}
            return {
                "strategy": strategy_name,
                "stop_loss": self.strategy_sl_tp[strategy_name]["stop_loss"],
                "take_profit": self.strategy_sl_tp[strategy_name]["take_profit"],
                "global_stop_loss": self.dynamic_stop_loss_percent,
                "global_take_profit": self.dynamic_take_profit_percent
            }
        else:
            return {
                "global_stop_loss": self.dynamic_stop_loss_percent,
                "global_take_profit": self.dynamic_take_profit_percent,
                "strategies": self.strategy_sl_tp.copy()
            }
    
    def calculate_stop_loss_take_profit(self, 
                                      strategy_name: str,
                                      current_price: float,
                                      action: str) -> tuple[float, float]:
        """
        Calculate stop loss and take profit levels for a strategy
        """
        if strategy_name not in self.strategy_sl_tp:
            # Use global settings as fallback
            sl_percent = self.dynamic_stop_loss_percent
            tp_percent = self.dynamic_take_profit_percent
        else:
            sl_percent = self.strategy_sl_tp[strategy_name]["stop_loss"]
            tp_percent = self.strategy_sl_tp[strategy_name]["take_profit"]
        
        if action == "buy":
            stop_loss = current_price * (1 - sl_percent / 100)
            take_profit = current_price * (1 + tp_percent / 100)
        elif action == "sell":
            stop_loss = current_price * (1 + sl_percent / 100)
            take_profit = current_price * (1 - tp_percent / 100)
        else:
            stop_loss = current_price
            take_profit = current_price
        
        return stop_loss, take_profit
    
    @classmethod
    def update_global_risk_settings(cls,
                                  stop_loss_percent: float = None,
                                  take_profit_percent: float = None):
        """
        Class method to update global risk settings
        Can be called from Colab cells
        """
        # This would need to be called on an instance
        # For now, we'll create a global instance
        if not hasattr(cls, '_global_instance'):
            cls._global_instance = cls()
        
        cls._global_instance.update_global_risk(stop_loss_percent, take_profit_percent)
    
    @classmethod
    def update_strategy_risk_settings(cls,
                                    strategy_name: str,
                                    stop_loss_percent: float = None,
                                    take_profit_percent: float = None):
        """
        Class method to update strategy risk settings
        Can be called from Colab cells
        """
        if not hasattr(cls, '_global_instance'):
            cls._global_instance = cls()
        
        cls._global_instance.update_strategy_risk(strategy_name, stop_loss_percent, take_profit_percent)
    
    @classmethod
    def get_current_risk_settings(cls) -> Dict[str, Any]:
        """
        Class method to get current risk settings
        Can be called from Colab cells
        """
        if not hasattr(cls, '_global_instance'):
            cls._global_instance = cls()
        
        return cls._global_instance.get_risk_settings()
