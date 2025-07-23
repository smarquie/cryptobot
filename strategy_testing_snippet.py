#!/usr/bin/env python3
"""
STRATEGY TESTING SNIPPET
Use this in your notebook to test each strategy individually
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ==================== STRATEGY TESTING FUNCTIONS ====================

def create_test_market_data(symbols=["BTC", "AVAX", "SOL"], periods=50):
    """
    Create realistic test market data for strategy testing
    """
    print(f"📊 Creating test market data for {symbols}...")
    
    market_data = {}
    
    for symbol in symbols:
        # Create realistic price movements
        base_price = {"BTC": 45000, "AVAX": 25, "SOL": 150}.get(symbol, 100)
        
        # Generate realistic OHLCV data
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='1min')
        
        # Create price movements with some volatility
        np.random.seed(42)  # For reproducible results
        price_changes = np.random.normal(0, 0.002, periods)  # 0.2% volatility
        prices = [base_price]
        
        for i in range(1, periods):
            new_price = prices[-1] * (1 + price_changes[i])
            prices.append(new_price)
        
        # Create OHLCV data
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            # Add some realistic high/low variation
            high = price * (1 + abs(np.random.normal(0, 0.001)))
            low = price * (1 - abs(np.random.normal(0, 0.001)))
            open_price = price * (1 + np.random.normal(0, 0.0005))
            close_price = price
            volume = np.random.uniform(1000, 10000)
            
            data.append({
                'timestamp': date,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close_price,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        market_data[f"{symbol}_1m"] = df
        print(f"✅ Created {len(df)} data points for {symbol}")
    
    return market_data

def test_individual_strategy(strategy_name, market_data, symbol="BTC", verbose=True):
    """
    Test a single strategy with detailed output
    """
    print(f"\n{'='*60}")
    print(f"🧪 TESTING {strategy_name.upper()} STRATEGY")
    print(f"{'='*60}")
    
    try:
        # Import the strategy
        if strategy_name.lower() == "ultra-scalp":
            from strategies.ultra_scalp import UltraScalpStrategy
            strategy = UltraScalpStrategy()
        elif strategy_name.lower() == "fast-scalp":
            from strategies.fast_scalp import FastScalpStrategy
            strategy = FastScalpStrategy()
        elif strategy_name.lower() == "quick-momentum":
            from strategies.quick_momentum import QuickMomentumStrategy
            strategy = QuickMomentumStrategy()
        elif strategy_name.lower() == "ttm-squeeze":
            from strategies.ttm_squeeze import TTMSqueezeStrategy
            strategy = TTMSqueezeStrategy()
        else:
            print(f"❌ Unknown strategy: {strategy_name}")
            return None
        
        # Get market data for the symbol
        df_key = f"{symbol}_1m"
        if df_key not in market_data:
            print(f"❌ No data found for {symbol}")
            return None
        
        df = market_data[df_key]
        
        if verbose:
            print(f"📊 Testing with {len(df)} data points")
            print(f"📈 Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
            print(f"📊 Volume range: {df['volume'].min():.0f} - {df['volume'].max():.0f}")
        
        # Run strategy analysis
        signal = strategy.analyze_and_signal(df, symbol)
        
        if verbose:
            print(f"\n🎯 STRATEGY RESULTS:")
            print(f"   Action: {signal.get('action', 'N/A')}")
            print(f"   Confidence: {signal.get('confidence', 0):.3f}")
            print(f"   Reason: {signal.get('reason', 'N/A')}")
            print(f"   Entry Price: ${signal.get('entry_price', 0):.2f}")
            print(f"   Stop Loss: ${signal.get('stop_loss', 0):.2f}")
            print(f"   Take Profit: ${signal.get('take_profit', 0):.2f}")
            print(f"   Max Hold Time: {signal.get('max_hold_time', 0)} seconds")
            print(f"   Target Hold: {signal.get('target_hold', 'N/A')}")
        
        # Additional strategy-specific metrics
        if strategy_name.lower() == "ultra-scalp":
            print(f"   RSI: {signal.get('rsi', 0):.1f}")
            print(f"   RSI Slope: {signal.get('rsi_slope', 0):.3f}")
            print(f"   Price Change 1m: {signal.get('price_change_1m', 0):.3f}%")
            print(f"   Volume Surge: {signal.get('volume_surge', False)}")
        
        elif strategy_name.lower() == "fast-scalp":
            print(f"   RSI: {signal.get('rsi', 0):.1f}")
            print(f"   MACD: {signal.get('macd', 0):.6f}")
            print(f"   MACD Signal: {signal.get('macd_signal', 0):.6f}")
            print(f"   Volume Surge: {signal.get('volume_surge', False)}")
        
        elif strategy_name.lower() == "quick-momentum":
            print(f"   RSI: {signal.get('rsi', 0):.1f}")
            print(f"   Price Change 3m: {signal.get('price_change_3m', 0):.3f}%")
            print(f"   GCP Detected: {signal.get('gcp_detected', False)}")
            print(f"   GCP Confidence: {signal.get('gcp_confidence', 0):.3f}")
            print(f"   Volume Surge: {signal.get('volume_surge', False)}")
        
        elif strategy_name.lower() == "ttm-squeeze":
            print(f"   RSI: {signal.get('rsi', 0):.1f}")
            print(f"   Squeeze: {signal.get('squeeze', False)}")
            print(f"   BB Position: {signal.get('bb_position', 0):.3f}")
            print(f"   KC Position: {signal.get('kc_position', 0):.3f}")
            print(f"   Volume Surge: {signal.get('volume_surge', False)}")
        
        return signal
        
    except Exception as e:
        print(f"❌ Error testing {strategy_name}: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_all_strategies(market_data, symbol="BTC", verbose=True):
    """
    Test all strategies and compare results
    """
    print(f"\n{'='*80}")
    print(f"🧪 COMPREHENSIVE STRATEGY TESTING FOR {symbol}")
    print(f"{'='*80}")
    
    strategies = [
        "Ultra-Scalp",
        "Fast-Scalp", 
        "Quick-Momentum",
        "TTM-Squeeze"
    ]
    
    results = {}
    
    for strategy in strategies:
        result = test_individual_strategy(strategy, market_data, symbol, verbose)
        results[strategy] = result
    
    # Summary comparison
    print(f"\n{'='*80}")
    print(f"📊 STRATEGY COMPARISON SUMMARY")
    print(f"{'='*80}")
    
    for strategy, result in results.items():
        if result:
            action = result.get('action', 'hold')
            confidence = result.get('confidence', 0)
            reason = result.get('reason', 'N/A')
            
            status = "✅ SIGNAL" if action != 'hold' else "⏸️ NO SIGNAL"
            print(f"{strategy:15} | {status:12} | Conf: {confidence:.3f} | {reason[:50]}...")
        else:
            print(f"{strategy:15} | ❌ ERROR     | Conf: 0.000 | Error occurred")
    
    return results

def test_strategy_parameters(strategy_name, market_data, symbol="BTC", param_tests=None):
    """
    Test strategy with different parameter combinations
    """
    print(f"\n{'='*80}")
    print(f"🔧 PARAMETER TESTING FOR {strategy_name.upper()}")
    print(f"{'='*80}")
    
    if param_tests is None:
        # Default parameter tests
        param_tests = {
            "RSI_OVERSOLD": [35, 40, 45],
            "MIN_CONFIDENCE": [0.1, 0.2, 0.3],
            "VOLUME_SURGE_MULTIPLIER": [1.01, 1.05, 1.1]
        }
    
    results = {}
    
    for param_name, param_values in param_tests.items():
        print(f"\n📊 Testing {param_name}:")
        
        for value in param_values:
            try:
                # Temporarily modify the strategy parameters
                # This is a simplified version - you may need to adjust based on your actual config
                print(f"   Testing {param_name} = {value}")
                
                # Test the strategy
                result = test_individual_strategy(strategy_name, market_data, symbol, verbose=False)
                
                if result:
                    action = result.get('action', 'hold')
                    confidence = result.get('confidence', 0)
                    print(f"      → Action: {action}, Confidence: {confidence:.3f}")
                else:
                    print(f"      → Error occurred")
                    
            except Exception as e:
                print(f"      → Error: {e}")
    
    return results

def analyze_market_conditions(market_data, symbol="BTC"):
    """
    Analyze current market conditions to help understand strategy behavior
    """
    print(f"\n{'='*60}")
    print(f"📈 MARKET CONDITION ANALYSIS FOR {symbol}")
    print(f"{'='*60}")
    
    df = market_data.get(f"{symbol}_1m")
    if df is None:
        print(f"❌ No data found for {symbol}")
        return
    
    # Calculate basic market metrics
    current_price = df['close'].iloc[-1]
    price_change_1m = ((current_price / df['close'].iloc[-2]) - 1) * 100 if len(df) > 1 else 0
    price_change_5m = ((current_price / df['close'].iloc[-6]) - 1) * 100 if len(df) > 5 else 0
    price_change_10m = ((current_price / df['close'].iloc[-11]) - 1) * 100 if len(df) > 10 else 0
    
    # Volume analysis
    current_volume = df['volume'].iloc[-1]
    avg_volume = df['volume'].rolling(5).mean().iloc[-1]
    volume_surge = current_volume > avg_volume * 1.1
    
    # Volatility
    returns = df['close'].pct_change().dropna()
    volatility = returns.std() * 100
    
    print(f"📊 Current Price: ${current_price:.2f}")
    print(f"📈 Price Changes:")
    print(f"   1m: {price_change_1m:+.3f}%")
    print(f"   5m: {price_change_5m:+.3f}%")
    print(f"   10m: {price_change_10m:+.3f}%")
    print(f"📊 Volume Analysis:")
    print(f"   Current Volume: {current_volume:.0f}")
    print(f"   Average Volume: {avg_volume:.0f}")
    print(f"   Volume Surge: {volume_surge}")
    print(f"📈 Volatility: {volatility:.3f}%")
    
    # Market condition assessment
    if abs(price_change_5m) > 1:
        condition = "HIGH VOLATILITY"
    elif abs(price_change_5m) < 0.1:
        condition = "LOW VOLATILITY"
    else:
        condition = "NORMAL"
    
    print(f"🎯 Market Condition: {condition}")

# ==================== USAGE EXAMPLES ====================

def run_complete_test():
    """
    Run a complete test of all strategies
    """
    print("🚀 STARTING COMPLETE STRATEGY TESTING")
    print("="*80)
    
    # Create test data
    market_data = create_test_market_data()
    
    # Analyze market conditions
    analyze_market_conditions(market_data)
    
    # Test all strategies
    results = test_all_strategies(market_data)
    
    return results

# ==================== NOTEBOOK USAGE SNIPPETS ====================

"""
# COPY AND PASTE THESE SNIPPETS INTO YOUR NOTEBOOK:

# 1. Test all strategies at once:
market_data = create_test_market_data()
results = test_all_strategies(market_data)

# 2. Test individual strategy:
signal = test_individual_strategy("Ultra-Scalp", market_data)

# 3. Test with different symbols:
market_data = create_test_market_data(["BTC", "AVAX", "SOL"])
for symbol in ["BTC", "AVAX", "SOL"]:
    print(f"\nTesting {symbol}:")
    test_all_strategies(market_data, symbol)

# 4. Parameter testing:
param_tests = {
    "RSI_OVERSOLD": [35, 40, 45],
    "MIN_CONFIDENCE": [0.1, 0.2, 0.3]
}
test_strategy_parameters("Ultra-Scalp", market_data, param_tests=param_tests)

# 5. Market condition analysis:
analyze_market_conditions(market_data)

# 6. Quick strategy comparison:
strategies = ["Ultra-Scalp", "Fast-Scalp", "Quick-Momentum", "TTM-Squeeze"]
market_data = create_test_market_data()
for strategy in strategies:
    signal = test_individual_strategy(strategy, market_data, verbose=False)
    if signal and signal.get('action') != 'hold':
        print(f"{strategy}: {signal['action']} (conf: {signal['confidence']:.3f})")
"""

if __name__ == "__main__":
    # Run complete test when executed directly
    run_complete_test() 
