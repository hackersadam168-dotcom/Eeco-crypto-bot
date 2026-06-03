"""Signal generation engine - Detects BUY LONG and SELL SHORT spikes."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from core.binance_api import BinanceAPIClient
from core.analyzer import MarketAnalyzer
from core.confidence_scorer import ConfidenceScorer
from database.db_manager import DatabaseManager
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class SignalEngine:
    """Generate trading signals based on market analysis."""
    
    def __init__(self, api_client: BinanceAPIClient = None, db_manager: DatabaseManager = None):
        """Initialize signal engine.
        
        Args:
            api_client: BinanceAPIClient instance
            db_manager: Database manager instance
        """
        self.api_client = api_client or BinanceAPIClient()
        self.analyzer = MarketAnalyzer()
        self.scorer = ConfidenceScorer()
        self.db = db_manager or DatabaseManager()
    
    def analyze_pair(self, symbol: str) -> Optional[Dict]:
        """Analyze a single trading pair across timeframes.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            
        Returns:
            Signal dict or None
        """
        try:
            # Fetch current price
            ticker = self.api_client.get_ticker(symbol)
            if not ticker:
                return None
            
            current_price = float(ticker.get('lastPrice', 0))
            if current_price == 0:
                return None
            
            # Analyze intraday (15m, 1h)
            intraday_signal = self._analyze_timeframe_group(
                symbol,
                settings.INTRADAY_INTERVALS,
                'INTRADAY',
                current_price
            )
            
            # Analyze swing (4h, 1d)
            swing_signal = self._analyze_timeframe_group(
                symbol,
                settings.SWING_INTERVALS,
                'SWING',
                current_price
            )
            
            # Return the highest confidence signal
            signals = [s for s in [intraday_signal, swing_signal] if s]
            if signals:
                return max(signals, key=lambda x: x['confidence'])
            
            return None
        except Exception as e:
            logger.debug(f"Error analyzing {symbol}: {str(e)}")
            return None
    
    def _analyze_timeframe_group(self, symbol: str, intervals: List[str], 
                                  signal_type: str, current_price: float) -> Optional[Dict]:
        """Analyze multiple timeframes for a signal.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            intervals: List of timeframe intervals ['15m', '1h']
            signal_type: 'INTRADAY' or 'SWING'
            current_price: Current price
            
        Returns:
            Signal dict or None
        """
        try:
            # Fetch candles for each timeframe
            tf_data = {}
            for interval in intervals:
                candles = self.api_client.get_candles(symbol, interval, limit=50)
                if candles:
                    tf_data[interval] = candles
            
            if not tf_data:
                return None
            
            # Analyze each timeframe
            tf_analyses = {}
            for interval, candles in tf_data.items():
                tf_analyses[interval] = self._analyze_single_timeframe(candles)
            
            # Determine signal direction (majority vote)
            bullish_count = sum(1 for a in tf_analyses.values() if a.get('direction') == 'BULLISH')
            bearish_count = sum(1 for a in tf_analyses.values() if a.get('direction') == 'BEARISH')
            
            if bullish_count > bearish_count:
                signal_direction = 'BUY LONG'
                is_bullish = True
            elif bearish_count > bullish_count:
                signal_direction = 'SELL SHORT'
                is_bullish = False
            else:
                return None
            
            # Calculate confidence scores
            scores = self._calculate_scores(symbol, tf_analyses, is_bullish, tf_data)
            confidence = self.scorer.calculate_overall_confidence(scores)
            
            # Check if signal meets threshold
            if not self.scorer.meets_threshold(confidence):
                return None
            
            # Check cooldown
            if self._is_on_cooldown(symbol, signal_direction):
                return None
            
            # Get risk level
            latest_candles = list(tf_data.values())[0]
            volatility = self.analyzer.calculate_volatility(latest_candles)
            structure = self.analyzer.detect_market_structure(latest_candles)
            risk_level = self.analyzer.get_risk_level(volatility, 0.0, structure)
            
            # Generate reason and bot view
            reason = self._generate_reason(scores, tf_analyses)
            bot_view = self._generate_bot_view(is_bullish, structure)
            
            signal = {
                'coin': symbol.replace('USDT', ''),
                'action': signal_direction,
                'type': signal_type,
                'confidence': int(confidence),
                'risk': risk_level,
                'reason': reason,
                'bot_view': bot_view,
                'price': current_price,
                'timeframe_group': f"{'/'.join(settings.INTRADAY_INTERVALS)}/{'/'.join(settings.SWING_INTERVALS)}",
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            return signal
        except Exception as e:
            logger.debug(f"Error analyzing timeframe group for {symbol}: {str(e)}")
            return None
    
    def _analyze_single_timeframe(self, candles: List[Dict]) -> Dict:
        """Analyze a single timeframe.
        
        Args:
            candles: List of candle data
            
        Returns:
            Analysis dict
        """
        is_bullish, trend_strength = self.analyzer.calculate_trend(candles)
        rvol = self.analyzer.calculate_relative_volume(candles)
        structure = self.analyzer.detect_market_structure(candles)
        volatility = self.analyzer.calculate_volatility(candles)
        has_spike, spike_strength = self.analyzer.detect_spike(candles)
        
        return {
            'direction': 'BULLISH' if is_bullish else 'BEARISH',
            'trend_strength': trend_strength,
            'rvol': rvol,
            'structure': structure,
            'volatility': volatility,
            'has_spike': has_spike,
            'spike_strength': spike_strength,
        }
    
    def _calculate_scores(self, symbol: str, tf_analyses: Dict, 
                          is_bullish: bool, tf_data: Dict) -> Dict:
        """Calculate component confidence scores.
        
        Args:
            symbol: Trading symbol
            tf_analyses: Timeframe analysis results
            is_bullish: True if bullish signal
            tf_data: Raw timeframe data
            
        Returns:
            Scores dict
        """
        # Average scores across timeframes
        avg_rvol = sum(a['rvol'] for a in tf_analyses.values()) / len(tf_analyses) if tf_analyses else 1.0
        avg_volatility = sum(a['volatility'] for a in tf_analyses.values()) / len(tf_analyses) if tf_analyses else 0.01
        
        # Check for spikes
        has_spike = any(a.get('has_spike', False) for a in tf_analyses.values())
        spike_strength = max([a.get('spike_strength', 0) for a in tf_analyses.values()])
        
        # Get latest candles for price expansion
        latest_candles = list(tf_data.values())[0] if tf_data else []
        price_change = self.analyzer.calculate_price_expansion(latest_candles) if latest_candles else 0.0
        
        # Count multi-timeframe alignment
        aligned = sum(1 for a in tf_analyses.values() 
                     if (a['direction'] == 'BULLISH' and is_bullish) or 
                        (a['direction'] == 'BEARISH' and not is_bullish))
        
        scores = {
            'price_expansion': self.scorer.calculate_price_expansion_score(price_change, 0.5),
            'relative_volume': self.scorer.calculate_volume_score(avg_rvol),
            'spike': self.scorer.calculate_spike_score(has_spike, spike_strength),
            'open_interest': 70.0,
            'trend': self.scorer.calculate_trend_score(is_bullish, sum(a['trend_strength'] for a in tf_analyses.values()) / len(tf_analyses) if tf_analyses else 0.5),
            'market_structure': self.scorer.calculate_structure_score(list(tf_analyses.values())[0]['structure'] if tf_analyses else 'range', is_bullish),
            'breakout_strength': self.scorer.calculate_breakout_score(max(a['trend_strength'] for a in tf_analyses.values()) if tf_analyses else 0.5),
        }
        
        return scores
    
    def _is_on_cooldown(self, symbol: str, action: str) -> bool:
        """Check if signal is on cooldown.
        
        Args:
            symbol: Trading symbol
            action: Signal action
            
        Returns:
            True if on cooldown
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=settings.COOLDOWN_HOURS)
            last_signal = self.db.get_last_signal(symbol.replace('USDT', ''), action)
            
            if last_signal:
                signal_time = datetime.fromisoformat(last_signal[10].replace('Z', '+00:00'))
                if signal_time > cutoff_time:
                    return True
            
            return False
        except Exception as e:
            logger.debug(f"Error checking cooldown: {str(e)}")
            return False
    
    def _generate_reason(self, scores: Dict, tf_analyses: Dict) -> List[str]:
        """Generate reason bullets for the signal.
        
        Args:
            scores: Confidence scores
            tf_analyses: Timeframe analysis results
            
        Returns:
            List of reason bullets
        """
        reasons = []
        
        try:
            # Volume reason
            avg_rvol = sum(a['rvol'] for a in tf_analyses.values()) / len(tf_analyses) if tf_analyses else 1.0
            if avg_rvol >= settings.VERY_HIGH_RVOL:
                reasons.append(f"🔥 RVOL {avg_rvol:.1f}x - Extreme volume spike!")
            elif avg_rvol >= settings.HIGH_RVOL:
                reasons.append(f"📈 RVOL {avg_rvol:.1f}x above average")
            
            # Spike reason
            if scores['spike'] >= 80:
                reasons.append("⚡ Price spike detected with high conviction")
            elif scores['spike'] >= 70:
                reasons.append("📊 Price spike detected across timeframes")
            
            # Trend reason
            if scores['trend'] >= 80:
                reasons.append("💪 Strong trend confirmation")
            
            # Structure reason
            structure = list(tf_analyses.values())[0]['structure'] if tf_analyses else 'range'
            if structure == 'bullish':
                reasons.append("📈 Bullish breakout confirmed")
            elif structure == 'bearish':
                reasons.append("📉 Bearish breakdown confirmed")
        except Exception as e:
            logger.debug(f"Error generating reason: {str(e)}")
        
        return reasons if reasons else ["Setup identified"]
    
    def _generate_bot_view(self, is_bullish: bool, structure: str) -> str:
        """Generate bot view explanation.
        
        Args:
            is_bullish: True if bullish
            structure: Market structure type
            
        Returns:
            Bot view text
        """
        if is_bullish:
            if structure == 'bullish':
                return "🚀 Strong bullish structure with breakout confirmation. Upside continuation favored."
            else:
                return "📈 Bullish momentum detected across multiple timeframes. Expect upside potential."
        else:
            if structure == 'bearish':
                return "📉 Bearish structure confirmed with breakdown. Downside continuation likely."
            else:
                return "🔻 Bearish momentum detected. Short opportunity with downside bias."
