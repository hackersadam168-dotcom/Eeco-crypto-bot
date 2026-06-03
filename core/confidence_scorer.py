"""Confidence scoring engine for signals."""
from typing import Dict, List
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class ConfidenceScorer:
    """Calculate confidence scores for trading signals."""
    
    def __init__(self):
        """Initialize confidence scorer."""
        self.weights = settings.CONFIDENCE_WEIGHTS
    
    def calculate_price_expansion_score(self, price_change: float, avg_change: float) -> float:
        """Score price expansion relative to historical average.
        
        Args:
            price_change: Current price change percentage
            avg_change: Average historical price change
            
        Returns:
            Score 0-100
        """
        if avg_change == 0:
            return 50.0
        
        ratio = abs(price_change) / abs(avg_change) if avg_change != 0 else 1.0
        
        if ratio > 2.0:
            return 90.0
        elif ratio > 1.5:
            return 75.0
        elif ratio > 1.0:
            return 60.0
        else:
            return 40.0
    
    def calculate_volume_score(self, rvol: float) -> float:
        """Score based on relative volume.
        
        Args:
            rvol: Relative volume (current / average)
            
        Returns:
            Score 0-100
        """
        if rvol >= settings.VERY_HIGH_RVOL:  # >= 5.0
            return 95.0
        elif rvol >= settings.HIGH_RVOL:  # >= 3.0
            return 85.0
        elif rvol >= settings.MIN_RVOL:  # >= 1.5
            return 70.0
        elif rvol >= 1.0:
            return 50.0
        else:
            return 30.0
    
    def calculate_oi_score(self, price_direction: str, oi_change: float) -> float:
        """Score based on open interest changes.
        
        Args:
            price_direction: 'up' or 'down'
            oi_change: OI change percentage
            
        Returns:
            Score 0-100
        """
        oi_change = abs(oi_change)
        
        if price_direction == 'up':
            # Price up + OI up = bullish participation
            if oi_change > 0.20:  # > 20%
                return 90.0
            elif oi_change > 0.10:  # > 10%
                return 75.0
            elif oi_change > 0.0:
                return 60.0
            else:
                # Price up + OI down = potential short covering (less bullish)
                return 40.0
        else:
            # Price down + OI up = bearish participation
            if oi_change > 0.20:
                return 90.0
            elif oi_change > 0.10:
                return 75.0
            elif oi_change > 0.0:
                return 60.0
            else:
                # Price down + OI down = weak trend
                return 30.0
    
    def calculate_trend_score(self, is_bullish: bool, trend_strength: float) -> float:
        """Score based on trend direction and strength.
        
        Args:
            is_bullish: True if bullish trend
            trend_strength: Strength 0-1
            
        Returns:
            Score 0-100
        """
        base_score = 50.0 if is_bullish else 50.0
        
        if trend_strength > 0.8:
            return 90.0 if is_bullish else 10.0
        elif trend_strength > 0.6:
            return 75.0 if is_bullish else 25.0
        elif trend_strength > 0.4:
            return 65.0 if is_bullish else 35.0
        else:
            return 55.0 if is_bullish else 45.0
    
    def calculate_structure_score(self, breakout_type: str, is_bullish: bool) -> float:
        """Score market structure (breakouts/breakdowns).
        
        Args:
            breakout_type: 'bullish', 'bearish', or 'range'
            is_bullish: True if signal is bullish
            
        Returns:
            Score 0-100
        """
        if breakout_type == 'bullish' and is_bullish:
            return 85.0
        elif breakout_type == 'bearish' and not is_bullish:
            return 85.0
        elif breakout_type == 'range':
            return 60.0
        else:
            return 40.0
    
    def calculate_breakout_score(self, breakout_strength: float) -> float:
        """Score breakout strength.
        
        Args:
            breakout_strength: Strength 0-1
            
        Returns:
            Score 0-100
        """
        if breakout_strength > 0.8:
            return 90.0
        elif breakout_strength > 0.6:
            return 75.0
        elif breakout_strength > 0.4:
            return 60.0
        else:
            return 40.0
    
    def calculate_multi_tf_score(self, tf_alignment_count: int, total_tfs: int) -> float:
        """Score multi-timeframe alignment.
        
        Args:
            tf_alignment_count: Number of aligned timeframes
            total_tfs: Total timeframes analyzed
            
        Returns:
            Score 0-100
        """
        alignment_ratio = tf_alignment_count / total_tfs
        
        if alignment_ratio == 1.0:  # All aligned
            return 95.0
        elif alignment_ratio >= 0.75:  # 3 out of 4
            return 80.0
        elif alignment_ratio >= 0.5:  # 2 out of 4
            return 65.0
        else:
            return 40.0
    
    def calculate_overall_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate overall confidence score using weighted average.
        
        Args:
            scores: Dict of component scores
                   Keys: 'price_expansion', 'relative_volume', 'open_interest',
                         'trend', 'market_structure', 'breakout_strength',
                         'multi_tf_alignment'
            
        Returns:
            Overall confidence 0-100
        """
        total_score = 0.0
        total_weight = 0.0
        
        for key, weight in self.weights.items():
            if key in scores:
                total_score += scores[key] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        final_score = total_score / total_weight
        return round(final_score, 2)
    
    def meets_threshold(self, confidence: float) -> bool:
        """Check if confidence meets minimum threshold.
        
        Args:
            confidence: Confidence score
            
        Returns:
            True if >= threshold
        """
        return confidence >= settings.CONFIDENCE_THRESHOLD
