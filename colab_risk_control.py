# Colab Risk Control Interface
# Copy this into a Colab cell to control stop loss and take profit levels

import sys
sys.path.append('cryptobot')

from utils.risk_manager import DynamicRiskManager

def update_global_risk(stop_loss_percent=None, take_profit_percent=None):
    """
    Update global stop loss and take profit levels
    
    Examples:
    # Make more conservative (tighter stops)
    update_global_risk(stop_loss_percent=0.3, take_profit_percent=0.6)
    
    # Make more aggressive (wider stops)
    update_global_risk(stop_loss_percent=1.0, take_profit_percent=2.0)
    
    # Check current settings
    get_current_risk_settings()
    """
    DynamicRiskManager.update_global_risk_settings(
        stop_loss_percent=stop_loss_percent,
        take_profit_percent=take_profit_percent
    )

def update_strategy_risk(strategy_name, stop_loss_percent=None, take_profit_percent=None):
    """
    Update risk settings for a specific strategy
    
    Examples:
    # Make Ultra-Scalp more conservative
    update_strategy_risk("Ultra-Scalp", stop_loss_percent=0.15, take_profit_percent=0.30)
    
    # Make TTM-Squeeze more aggressive
    update_strategy_risk("TTM-Squeeze", stop_loss_percent=1.0, take_profit_percent=2.0)
    """
    DynamicRiskManager.update_strategy_risk_settings(
        strategy_name=strategy_name,
        stop_loss_percent=stop_loss_percent,
        take_profit_percent=take_profit_percent
    )

def get_current_risk_settings():
    """Get current risk settings for all strategies"""
    settings = DynamicRiskManager.get_current_risk_settings()
    
    print("🛡️ Current Risk Settings:")
    print(f"   Global Stop Loss: {settings['global_stop_loss']}%")
    print(f"   Global Take Profit: {settings['global_take_profit']}%")
    print("\n📊 Strategy-Specific Settings:")
    
    for strategy, risk in settings['strategies'].items():
        print(f"   {strategy}:")
        print(f"      Stop Loss: {risk['stop_loss']}%")
        print(f"      Take Profit: {risk['take_profit']}%")
    
    return settings

def make_conservative():
    """Make all strategies more conservative (tighter stops)"""
    print("🛡️ Making all strategies more conservative...")
    
    # Update global settings
    update_global_risk(stop_loss_percent=0.3, take_profit_percent=0.6)
    
    # Update individual strategies
    update_strategy_risk("Ultra-Scalp", stop_loss_percent=0.15, take_profit_percent=0.30)
    update_strategy_risk("Fast-Scalp", stop_loss_percent=0.20, take_profit_percent=0.40)
    update_strategy_risk("Quick-Momentum", stop_loss_percent=0.25, take_profit_percent=0.50)
    update_strategy_risk("TTM-Squeeze", stop_loss_percent=0.30, take_profit_percent=0.60)
    
    print("✅ All strategies set to conservative mode")

def make_aggressive():
    """Make all strategies more aggressive (wider stops)"""
    print("🚀 Making all strategies more aggressive...")
    
    # Update global settings
    update_global_risk(stop_loss_percent=1.0, take_profit_percent=2.0)
    
    # Update individual strategies
    update_strategy_risk("Ultra-Scalp", stop_loss_percent=0.50, take_profit_percent=1.00)
    update_strategy_risk("Fast-Scalp", stop_loss_percent=0.60, take_profit_percent=1.20)
    update_strategy_risk("Quick-Momentum", stop_loss_percent=0.80, take_profit_percent=1.60)
    update_strategy_risk("TTM-Squeeze", stop_loss_percent=1.00, take_profit_percent=2.00)
    
    print("✅ All strategies set to aggressive mode")

def reset_to_default():
    """Reset all risk settings to default values"""
    print("🔄 Resetting all risk settings to default...")
    
    # Reset global settings
    update_global_risk(stop_loss_percent=0.5, take_profit_percent=1.0)
    
    # Reset individual strategies
    update_strategy_risk("Ultra-Scalp", stop_loss_percent=0.25, take_profit_percent=0.50)
    update_strategy_risk("Fast-Scalp", stop_loss_percent=0.30, take_profit_percent=0.60)
    update_strategy_risk("Quick-Momentum", stop_loss_percent=0.40, take_profit_percent=0.80)
    update_strategy_risk("TTM-Squeeze", stop_loss_percent=0.50, take_profit_percent=1.00)
    
    print("✅ All risk settings reset to default")

def show_examples():
    """Show usage examples"""
    print("""
🎯 RISK CONTROL EXAMPLES:

# 1. Check current settings
get_current_risk_settings()

# 2. Make all strategies conservative (tighter stops)
make_conservative()

# 3. Make all strategies aggressive (wider stops)
make_aggressive()

# 4. Reset to default settings
reset_to_default()

# 5. Update global settings only
update_global_risk(stop_loss_percent=0.4, take_profit_percent=0.8)

# 6. Update specific strategy
update_strategy_risk("Ultra-Scalp", stop_loss_percent=0.20, take_profit_percent=0.40)

# 7. Quick adjustments
update_global_risk(stop_loss_percent=0.3)  # Just change stop loss
update_global_risk(take_profit_percent=1.5)  # Just change take profit
    """)

# Initialize and show current settings
print("🛡️ Risk Control Interface Loaded!")
print("📊 Current risk settings:")
get_current_risk_settings()
print("\n💡 Use show_examples() to see all available commands")
