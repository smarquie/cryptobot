#!/usr/bin/env python3
"""
PURE GCP MOMENTUM STRATEGY MODULE
GCP Pattern Detection as PRIMARY trading logic
Technical indicators used ONLY for confirmation/filtering
No RSI fallback - GCP or no trade

DESIGN PRINCIPLE:
- GCP pattern detection is the MAIN and ONLY entry trigger
- RSI/EMA/momentum used only to CONFIRM or FILTER GCP signals
- If no GCP pattern detected = NO TRADE (no fallback)
- Maintains exact compatibility with existing framework
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from cryptobot.config import BotConfig

class PureGCPDetector:
    """Pure GCP Pattern Detector - GCP is the only trade trigger"""
    
    def __init__(self):
        self.name = "Pure-GCP-Detector"
        self.pattern_history = {}
        
        # GCP-focused configuration
        self.config = {
            # Pattern detection windows
            "growth_detection_window": 20,
            "plateau_detection_window": 15,
            
            # GCP pattern requirements (more permissive for crypto)
            "min_growth_percentage": 0.12,  # Lower for more GCP opportunities
            "growth_consistency_threshold": 0.35,  # More permissive
            "plateau_volatility_threshold": 0.7,   # Higher tolerance
            "plateau_drift_threshold": 0.5,        # Higher tolerance
            "min_plateau_duration": 4,             # Shorter duration
            
            # GCP confidence thresholds
            "min_pattern_confidence": 0.25,  # Lower for more GCP signals
            "strong_pattern_confidence": 0.5,  # Strong pattern threshold
            
            # Technical confirmation settings
            "use_technical_confirmation": True,
            "confirmation_weight": 0.3,  # 30% weight to technical confirmation
            "gcp_weight": 0.7,          # 70% weight to GCP pattern
        }
    
    def _calculate_growth_score(self, prices: np.ndarray) -> float:
        """Calculate growth consistency score"""
        if len(prices) < 3:
            return 0.0
        price_changes = np.diff(prices)
        if len(price_changes) == 0:
            return 0.0
        consistency = np.mean(price_changes > 0) if np.mean(price_changes) > 0 else np.mean(price_changes < 0)
        return max(consistency, 1 - consistency)
    
    def _calculate_plateau_score(self, prices: np.ndarray) -> float:
        """Calculate plateau stability score"""
        if len(prices) < 3:
            return 0.0
        if np.mean(prices) == 0:
            return 0.0
            
        volatility = np.std(prices) / np.mean(prices)
        drift = abs(np.polyfit(np.arange(len(prices)), prices, 1)[0]) / np.mean(prices)
        
        volatility_score = max(0, 1 - (volatility / self.config["plateau_volatility_threshold"]))
        drift_score = max(0, 1 - (drift / self.config["plateau_drift_threshold"]))
        return (volatility_score * 0.6) + (drift_score * 0.4)  # Weight volatility more
    
    def _detect_growth_phase(self, prices: np.ndarray) -> Dict:
        """Detect growth/decline phase with flexible windows"""
        max_window = self.config["growth_detection_window"]
        if len(prices) < 5:
            return {"detected": False, "score": 0.0, "total_growth": 0.0}
        
        best_growth = 0.0
        best_score = 0.0
        best_window_size = 0
        
        # Try different window sizes to find the best growth pattern
        for window_size in range(5, min(len(prices), max_window) + 1):
            growth_window = prices[-window_size:]
            total_growth = (growth_window[-1] - growth_window[0]) / growth_window[0] * 100
            growth_score = self._calculate_growth_score(growth_window)
            
            if (abs(total_growth) >= self.config["min_growth_percentage"] and 
                growth_score >= self.config["growth_consistency_threshold"]):
                if abs(total_growth) > abs(best_growth):
                    best_growth = total_growth
                    best_score = growth_score
                    best_window_size = window_size
        
        return {
            "detected": best_window_size > 0,
            "score": best_score,
            "total_growth": best_growth,
            "window_size": best_window_size
        }
    
    def _detect_plateau_phase(self, prices: np.ndarray) -> Dict:
        """Detect plateau/consolidation phase"""
        max_window = self.config["plateau_detection_window"]
        if len(prices) < 4:
            return {"detected": False, "score": 0.0}
        
        best_score = 0.0
        best_window_size = 0
        
        for window_size in range(4, min(len(prices), max_window) + 1):
            plateau_window = prices[-window_size:]
            plateau_score = self._calculate_plateau_score(plateau_window)
            
            if (plateau_score >= 0.25 and  # Lower threshold for more patterns
                window_size >= self.config["min_plateau_duration"]):
                if plateau_score > best_score:
                    best_score = plateau_score
                    best_window_size = window_size
        
        return {
            "detected": best_window_size > 0,
            "score": best_score,
            "duration": best_window_size
        }
    
    def _get_technical_confirmation(self, df: pd.DataFrame) -> Dict:
        """Get technical indicator confirmation (OPTIONAL enhancement only)"""
        try:
            close = df['close']
            volume = df['volume'] if 'volume' in df.columns else pd.Series([1]*len(df))
            
            current_price = float(close.iloc[-1])
            
            # RSI for momentum confirmation (not entry trigger)
            rsi = self._calculate_rsi(close, 14)
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
            
            # EMA alignment for trend confirmation
            ema_fast = self._calculate_ema(close, 5)
            ema_slow = self._calculate_ema(close, 13)
            current_ema_fast = float(ema_fast.iloc[-1]) if not pd.isna(ema_fast.iloc[-1]) else current_price
            current_ema_slow = float(ema_slow.iloc[-1]) if not pd.isna(ema_slow.iloc[-1]) else current_price
            
            # Volume confirmation
            volume_avg = volume.rolling(10).mean().iloc[-1] if len(volume) >= 10 else volume.iloc[-1]
            volume_ratio = float(volume.iloc[-1]) / float(volume_avg) if volume_avg > 0 else 1.0
            
            # Calculate confirmation score (0.0 to 1.0)
            confirmation_score = 0.0
            confirmation_reasons = []
            
            # RSI momentum confirmation (not overbought/oversold trigger)
            if 25 <= current_rsi <= 75:  # Healthy RSI range
                confirmation_score += 0.3
                confirmation_reasons.append(f"RSI healthy: {current_rsi:.1f}")
            
            # EMA trend confirmation
            if current_ema_fast > current_ema_slow:  # Bullish trend
                confirmation_score += 0.4
                confirmation_reasons.append("EMA trend bullish")
            elif current_ema_fast < current_ema_slow:  # Bearish trend  
                confirmation_score += 0.4
                confirmation_reasons.append("EMA trend bearish")
            
            # Volume confirmation
            if volume_ratio > 1.1:  # Above average volume
                confirmation_score += 0.3
                confirmation_reasons.append(f"Volume surge: {volume_ratio:.2f}x")
            
            return {
                "score": min(1.0, confirmation_score),
                "reasons": confirmation_reasons,
                "rsi": current_rsi,
                "ema_trend": "bullish" if current_ema_fast > current_ema_slow else "bearish",
                "volume_ratio": volume_ratio
            }
            
        except Exception as e:
            return {"score": 0.5, "reasons": [f"Confirmation error: {e}"], "rsi": 50, "ema_trend": "neutral", "volume_ratio": 1.0}
    
    def detect_gcp(self, df: pd.DataFrame) -> Dict:
        """
        MAIN GCP DETECTION - GCP pattern is the ONLY trade trigger
        Technical indicators used ONLY for confirmation/filtering
        """
        try:
            if df.empty or len(df) < 15:
                return {
                    'detected': False, 
                    'confidence': 0.0, 
                    'reason': 'Insufficient data for GCP analysis',
                    'action': 'hold',
                    'pattern_strength': 'none'
                }
            
            close_prices = df["close"].values
            current_price = close_prices[-1]
            
            # STEP 1: DETECT GCP PATTERN (PRIMARY REQUIREMENT)
            split_point = max(6, len(close_prices) // 2)
            
            # Look for growth/decline in earlier data
            growth_result = self._detect_growth_phase(close_prices[:split_point])
            # Look for plateau in recent data
            plateau_result = self._detect_plateau_phase(close_prices[split_point:])
            
            # NO GCP PATTERN = NO TRADE
            if not (growth_result["detected"] and plateau_result["detected"]):
                return {
                    'detected': False,
                    'confidence': 0.0,
                    'reason': f'No GCP pattern: Growth={growth_result["detected"]}, Plateau={plateau_result["detected"]}',
                    'action': 'hold',
                    'pattern_strength': 'none',
                    'growth_phase': growth_result["detected"],
                    'plateau_phase': plateau_result["detected"]
                }
            
            # STEP 2: CALCULATE GCP PATTERN STRENGTH
            gcp_confidence = (growth_result["score"] + plateau_result["score"]) / 2
            pattern_direction = "bullish" if growth_result["total_growth"] > 0 else "bearish"
            action = "buy" if pattern_direction == "bullish" else "sell"
            
            # Check minimum GCP confidence
            if gcp_confidence < self.config["min_pattern_confidence"]:
                return {
                    'detected': False,
                    'confidence': gcp_confidence,
                    'reason': f'GCP pattern too weak: {gcp_confidence:.3f} < {self.config["min_pattern_confidence"]}',
                    'action': 'hold',
                    'pattern_strength': 'weak',
                    'raw_gcp_confidence': gcp_confidence
                }
            
            # STEP 3: TECHNICAL CONFIRMATION (OPTIONAL ENHANCEMENT)
            technical_conf = self._get_technical_confirmation(df)
            
            # Combine GCP strength with technical confirmation
            if self.config["use_technical_confirmation"]:
                final_confidence = (
                    gcp_confidence * self.config["gcp_weight"] + 
                    technical_conf["score"] * self.config["confirmation_weight"]
                )
            else:
                final_confidence = gcp_confidence
            
            # Cap confidence at reasonable level
            final_confidence = min(0.85, final_confidence)
            
            # Pattern strength classification
            if final_confidence >= self.config["strong_pattern_confidence"]:
                pattern_strength = "strong"
            elif final_confidence >= self.config["min_pattern_confidence"]:
                pattern_strength = "moderate"
            else:
                pattern_strength = "weak"
            
            # Build comprehensive reason
            reason_parts = [
                f"GCP {pattern_direction.upper()} pattern",
                f"Growth: {growth_result['total_growth']:.2f}% over {growth_result['window_size']}p",
                f"Plateau: {plateau_result['score']:.2f} stability over {plateau_result['duration']}p"
            ]
            
            if self.config["use_technical_confirmation"] and technical_conf["reasons"]:
                reason_parts.append(f"Confirmed by: {', '.join(technical_conf['reasons'][:2])}")
            
            reason = " | ".join(reason_parts)
            
            return {
                'detected': True,
                'confidence': final_confidence,
                'reason': reason,
                'action': action,
                'pattern_strength': pattern_strength,
                'pattern_direction': pattern_direction,
                'gcp_confidence': gcp_confidence,
                'technical_confirmation': technical_conf["score"],
                'growth_details': {
                    'growth_pct': growth_result["total_growth"],
                    'growth_score': growth_result["score"],
                    'window_size': growth_result["window_size"]
                },
                'plateau_details': {
                    'plateau_score': plateau_result["score"], 
                    'duration': plateau_result["duration"]
                },
                'technical_details': technical_conf
            }
            
        except Exception as e:
            return {
                'detected': False, 
                'confidence': 0.0, 
                'reason': f'GCP analysis error: {e}',
                'action': 'hold',
                'pattern_strength': 'error'
            }
    
    def _calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate EMA"""
        return data.ewm(span=period, adjust=False).mean()
    
    def _calculate_rsi(self, data: pd.Series, period: int) -> pd.Series:
        """Calculate RSI"""
        try:
            delta = data.diff()
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            
            avg_gains = gains.ewm(span=period, adjust=False).mean()
            avg_losses = losses.ewm(span=period, adjust=False).mean()
            
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.fillna(50)
        except Exception as e:
            return pd.Series([50] * len(data), index=data.index)


class QuickMomentumStrategy:
    """
    PURE GCP MOMENTUM STRATEGY
    
    DESIGN PRINCIPLE:
    - GCP pattern detection is the ONLY trade trigger
    - No RSI fallback, no alternative entry methods
    - Technical indicators used ONLY for confirmation/enhancement
    - GCP or no trade - period
    
    MAINTAINS EXACT COMPATIBILITY:
    - Same class name and interface
    - Same return format  
    - Same BotConfig integration
    - Works as drop-in replacement
    """
    
    def __init__(self):
        self.name = "Quick-Momentum"  # SAME name for compatibility
        self.gcp_detector = PureGCPDetector()  # NOW the ONLY trading logic
        
    def analyze_and_signal(self, df: pd.DataFrame, symbol: str) -> Dict:
        """
        PURE GCP ANALYSIS - GCP pattern or no trade
        SAME INTERFACE as original but GCP-focused logic
        """
        try:
            if df.empty or len(df) < 15:  # Need sufficient data for GCP
                return self._empty_signal('Insufficient data for GCP pattern analysis')

            close = df['close']
            current_price = float(close.iloc[-1])
            
            # ONLY GCP PATTERN DETECTION - no fallback logic
            gcp_result = self.gcp_detector.detect_gcp(df)
            
            # NO GCP PATTERN = NO TRADE
            if not gcp_result['detected']:
                return self._create_hold_signal(current_price, gcp_result['reason'])
            
            # GCP PATTERN DETECTED - prepare trade signal
            action = gcp_result['action']  # 'buy' or 'sell' from GCP
            confidence = gcp_result['confidence']
            
            # Check against minimum confidence from BotConfig
            if confidence < BotConfig.MOMENTUM_MIN_CONFIDENCE:
                return self._create_hold_signal(
                    current_price, 
                    f"GCP pattern confidence too low: {confidence:.3f} < {BotConfig.MOMENTUM_MIN_CONFIDENCE}"
                )
            
            # Calculate stop loss and take profit using BotConfig
            if action == 'buy':
                stop_loss = current_price * (1 - BotConfig.MOMENTUM_STOP_LOSS)
                take_profit = current_price * (1 + BotConfig.MOMENTUM_PROFIT_TARGET)
            else:  # sell
                stop_loss = current_price * (1 + BotConfig.MOMENTUM_STOP_LOSS)
                take_profit = current_price * (1 - BotConfig.MOMENTUM_PROFIT_TARGET)
            
            # Enhanced reason with GCP details
            reason = f"PURE GCP {action.upper()}: {gcp_result['reason']}"
            
            # SAME return format as original but GCP-driven
            return {
                'action': action,
                'confidence': confidence,
                'strategy': self.name,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'reason': reason,
                'max_hold_time': BotConfig.MOMENTUM_MAX_HOLD_SECONDS,
                'target_hold': f'{BotConfig.MOMENTUM_MAX_HOLD_SECONDS//60} minutes',
                
                # GCP-specific information (bonus fields)
                'gcp_pattern_detected': True,
                'pattern_strength': gcp_result['pattern_strength'],
                'pattern_direction': gcp_result['pattern_direction'],
                'gcp_confidence': gcp_result['gcp_confidence'],
                'technical_confirmation': gcp_result.get('technical_confirmation', 0.0),
                'growth_pct': gcp_result['growth_details']['growth_pct'],
                'plateau_duration': gcp_result['plateau_details']['duration'],
                
                # Technical details for monitoring
                'rsi': gcp_result['technical_details'].get('rsi', 50),
                'ema_trend': gcp_result['technical_details'].get('ema_trend', 'neutral'),
                'volume_ratio': gcp_result['technical_details'].get('volume_ratio', 1.0)
            }

        except Exception as e:
            return self._empty_signal(f'GCP strategy error: {e}')

    def _create_hold_signal(self, current_price: float, reason: str) -> Dict:
        """Create hold signal with current price"""
        return {
            'action': 'hold',
            'confidence': 0.0,
            'strategy': self.name,
            'entry_price': current_price,
            'stop_loss': current_price,
            'take_profit': current_price,
            'reason': reason,
            'max_hold_time': BotConfig.MOMENTUM_MAX_HOLD_SECONDS,
            'target_hold': f'{BotConfig.MOMENTUM_MAX_HOLD_SECONDS//60} minutes',
            'gcp_pattern_detected': False,
            'pattern_strength': 'none'
        }

    def _empty_signal(self, reason: str) -> Dict:
        """SAME empty signal format as original"""
        return {
            'action': 'hold',
            'confidence': 0.0,
            'strategy': self.name,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'reason': reason,
            'max_hold_time': BotConfig.MOMENTUM_MAX_HOLD_SECONDS,
            'target_hold': f'{BotConfig.MOMENTUM_MAX_HOLD_SECONDS//60} minutes',
            'gcp_pattern_detected': False,
            'pattern_strength': 'insufficient_data'
        }

# Export the strategy class - SAME as original
__all__ = ['QuickMomentumStrategy']
