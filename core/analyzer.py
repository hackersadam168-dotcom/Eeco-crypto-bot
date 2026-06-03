"""Market data analyzer for technical analysis."""
from typing import Dict, List, Tuple, Optional
import statistics
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class MarketAnalyzer:
    """Perform technical analysis on market data."""
    
    @staticmethod
    def parse_candle(candle: List) -> Dict:
        """Parse OKX candle data.
        
        Args:
            candle: [timestamp, open, high, low, close, volume, ...]
            
        Returns:
            Dict with candle data
        """
        return {
            'timestamp': int(candle[0]),
            'open': float(candle[1]),
            'high': float(candle[2]),
            'low': float(candle[3]),
            'close': float(candle[4]),
            'volume': float(candle[5]),
        }
    
    @staticmethod
    def calculate_trend(candles: List[Dict]) -> Tuple[bool, float]:
        """Determine trend direction and strength.
        
        Args:
            candles: List of candle data
            
        Returns:
            (is_bullish, strength_0_to_1)
        """
        if len(candles) < 2:
            return True, 0.5
        
        closes = [c['close'] for c in candles]
        current = closes[-1]
        previous = closes[-2]
        
        # Simple trend: price above or below moving average
        sma = statistics.mean(closes[-10:]) if len(closes) >= 10 else statistics.mean(closes)
        is_bullish = current > sma
        
        # Strength based on distance from SMA
        max_price = max(closes)
        min_price = min(closes)
        price_range = max_price - min_price
        
        if price_range == 0:
            strength = 0.5
        else:
            distance = abs(current - sma)
            strength = min(distance / price_range, 1.0)
        
        return is_bullish, strength
    
    @staticmethod
    def calculate_relative_volume(candles: List[Dict], lookback: int = 20) -> float:
        """Calculate relative volume (RVOL).
        
        Args:
            candles: List of candle data
            lookback: Number of candles for average
            
        Returns:
            RVOL ratio
        """
        if len(candles) < 2:
            return 1.0
        
        current_volume = candles[-1]['volume']
        avg_volume = statistics.mean([c['volume'] for c in candles[-lookback:]])
        
        if avg_volume == 0:
            return 1.0
        
        return current_volume / avg_volume
    
    @staticmethod
    def detect_market_structure(candles: List[Dict]) -> str:
        """Detect market structure (breakout/breakdown/range).
        
        Args:
            candles: List of candle data
            
        Returns:
            'bullish', 'bearish', or 'range'
        """
        if len(candles) < 10:
            return 'range'
        
        current_close = candles[-1]['close']
        
        # Find highest high and lowest low from last 20 candles
        recent = candles[-20:]
        highest_high = max(c['high'] for c in recent)
        lowest_low = min(c['low'] for c in recent)
        
        # Find previous support/resistance from candles before last 20
        if len(candles) > 20:
            previous = candles[-40:-20]
            prev_high = max(c['high'] for c in previous)
            prev_low = min(c['low'] for c in previous)
        else:
            prev_high = highest_high
            prev_low = lowest_low
        
        # Bullish breakout: price above previous major high
        if current_close > prev_high:
            return 'bullish'
        # Bearish breakdown: price below previous major low
        elif current_close < prev_low:
            return 'bearish'
        # Range bound
        else:
            return 'range'
    
    @staticmethod
    def calculate_volatility(candles: List[Dict], lookback: int = 14) -> float:
        """Calculate price volatility (standard deviation of returns).
        
        Args:
            candles: List of candle data
            lookback: Number of candles for calculation
            
        Returns:
            Volatility as percentage
        """
        if len(candles) < 2:
            return 0.0
        
        recent = candles[-lookback:]
        closes = [c['close'] for c in recent]
        
        returns = []
        for i in range(1, len(closes)):
            ret = (closes[i] - closes[i-1]) / closes[i-1]
            returns.append(ret)
        
        if len(returns) < 2:
            return 0.0
        
        volatility = statistics.stdev(returns)
        return abs(volatility)  # Convert to percentage
    
    @staticmethod
    def calculate_price_expansion(candles: List[Dict], lookback: int = 20) -> float:
        """Calculate price expansion ratio.
        
        Args:
            candles: List of candle data
            lookback: Number of candles for average
            
        Returns:
            Price change percentage
        """
        if len(candles) < 2:
            return 0.0
        
        current_close = candles[-1]['close']
        previous_close = candles[-2]['close']
        
        change = ((current_close - previous_close) / previous_close) * 100
        return change
    
    @staticmethod
    def calculate_oi_change(current_oi: float, previous_oi: float) -> float:
        """Calculate open interest change percentage.
        
        Args:
            current_oi: Current open interest
            previous_oi: Previous open interest
            
        Returns:
            OI change percentage
        """
        if previous_oi == 0:
            return 0.0
        
        return ((current_oi - previous_oi) / previous_oi) * 100
    
    @staticmethod
    def get_risk_level(volatility: float, oi_change: float, structure: str) -> str:
        """Determine risk level based on market conditions.
        
        Args:
            volatility: Price volatility
            oi_change: OI change percentage
            structure: Market structure type
            
        Returns:
            'LOW', 'MEDIUM', or 'HIGH'
        """
        thresholds = settings.RISK_THRESHOLDS
        
        # HIGH risk if high volatility and weak OI
        if volatility > thresholds['medium']['volatility_max']:
            if abs(oi_change) < thresholds['medium']['oi_change_min']:
                return 'HIGH'
        
        # LOW risk if low volatility and strong OI
        if volatility <= thresholds['low']['volatility_max']:
            if abs(oi_change) >= thresholds['low']['oi_change_min']:
                return 'LOW'
        
        # DEFAULT to MEDIUM
        return 'MEDIUM'
