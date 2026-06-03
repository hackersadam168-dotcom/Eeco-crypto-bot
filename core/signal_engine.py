"""Signal generation engine."""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from core.okx_api import OKXAPIClient
from core.analyzer import MarketAnalyzer
from core.confidence_scorer import ConfidenceScorer
from database.db_manager import DatabaseManager
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class SignalEngine:
    """Generate trading signals based on market analysis."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize signal engine.
        
        Args:
            db_manager: Database manager instance
        """
        self.api_client = OKXAPIClient()
        self.analyzer = MarketAnalyzer()
        self.scorer = ConfidenceScorer()
        self.db = db_manager or DatabaseManager()
    
    def analyze_pair(self, inst_id: str) -> Optional[Dict]:
        """Analyze a single trading pair across timeframes.
        
        Args:
            inst_id: Instrument ID
            
        Returns:
            Signal dict or None
        """
        try:
            # Fetch market data
            ticker = self.api_client.get_ticker(inst_id)
            if not ticker:
                return None
            
            current_price = float(ticker['last'])
            
            # Analyze intraday (15m, 1H)
            intraday_signal = self._analyze_timeframe_group(
                inst_id,
                settings.INTRADAY_TIMEFRAMES,
                'INTRADAY',
                current_price
            )
            
            # Analyze swing (4H, 1D)
            swing_signal = self._analyze_timeframe_group(
                inst_id,
                settings.SWING_TIMEFRAMES,
                'SWING',
                current_price
            )
            
            # Return the highest confidence signal
            signals = [s for s in [intraday_signal, swing_signal] if s]
            if signals:
                return max(signals, key=lambda x: x['confidence'])
            
            return None
        except Exception as e:
            logger.error(f"Error analyzing {inst_id}: {str(e)}")
            return None
    
    def _analyze_timeframe_group(self, inst_id: str, timeframes: List[int], 
                                 signal_type: str, current_price: float) -> Optional[Dict]:
        """Analyze multiple timeframes for a signal.
        
        Args:
            inst_id: Instrument ID
            timeframes: List of timeframes to analyze
            signal_type: 'INTRADAY' or 'SWING'
            current_price: Current price
            
        Returns:
            Signal dict or None
        """
        try:
            # Fetch candles for each timeframe
            tf_data = {}
            for tf in timeframes:
                candles = self.api_client.get_candles(inst_id, tf, limit=50)
                if candles:
                    tf_data[tf] = [self.analyzer.parse_candle(c) for c in candles]
            
            if not tf_data:
                return None
            
            # Analyze each timeframe
            tf_analyses = {}
            for tf, candles in tf_data.items():
                tf_analyses[tf] = self._analyze_single_timeframe(candles)
            
            # Calculate multi-timeframe alignment
            aligned_count = sum(1 for analysis in tf_analyses.values() 
                               if analysis.get('direction') in ['BULLISH', 'BEARISH'])
            
            # Determine signal direction
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
            scores = self._calculate_scores(inst_id, tf_analyses, is_bullish, tf_data)
            confidence = self.scorer.calculate_overall_confidence(scores)
            
            # Check if signal meets threshold
            if not self.scorer.meets_threshold(confidence):
                return None
            
            # Check cooldown
            if self._is_on_cooldown(inst_id, signal_direction):
                return None
            
            # Get risk level
            latest_candles = list(tf_data.values())[0]
            volatility = self.analyzer.calculate_volatility(latest_candles)
            oi_change = 0  # TODO: Get from API
            structure = self.analyzer.detect_market_structure(latest_candles)
            risk_level = self.analyzer.get_risk_level(volatility, oi_change, structure)
            
            # Generate reason and bot view
            reason = self._generate_reason(scores, tf_analyses)
            bot_view = self._generate_bot_view(is_bullish, structure)
            
            signal = {
                'coin': inst_id.replace('-USDT-SWAP', ''),
                'action': signal_direction,
                'type': signal_type,
                'confidence': confidence,
                'risk': risk_level,
                'reason': reason,
                'bot_view': bot_view,
                'price': current_price,
                'timeframe_group': f"{timeframes[0]}m/{timeframes[-1]}m",
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            return signal
        except Exception as e:
            logger.error(f"Error analyzing timeframe group for {inst_id}: {str(e)}")
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
        
        return {
            'direction': 'BULLISH' if is_bullish else 'BEARISH',
            'trend_strength': trend_strength,
            'rvol': rvol,
            'structure': structure,
            'volatility': volatility,
        }
    
    def _calculate_scores(self, inst_id: str, tf_analyses: Dict, 
                         is_bullish: bool, tf_data: Dict) -> Dict:
        """Calculate component confidence scores.
        
        Args:
            inst_id: Instrument ID
            tf_analyses: Timeframe analysis results
            is_bullish: True if bullish signal
            tf_data: Raw timeframe data
            
        Returns:
            Scores dict
        """
        # Average scores across timeframes
        avg_rvol = sum(a['rvol'] for a in tf_analyses.values()) / len(tf_analyses)
        avg_volatility = sum(a['volatility'] for a in tf_analyses.values()) / len(tf_analyses)
        
        # Get latest candles for price expansion
        latest_candles = list(tf_data.values())[0]
        price_change = self.analyzer.calculate_price_expansion(latest_candles)
        
        # Count multi-timeframe alignment
        aligned = sum(1 for a in tf_analyses.values() 
                     if (a['direction'] == 'BULLISH' and is_bullish) or 
                        (a['direction'] == 'BEARISH' and not is_bullish))
        
        scores = {
            'price_expansion': self.scorer.calculate_price_expansion_score(price_change, 0.5),
            'relative_volume': self.scorer.calculate_volume_score(avg_rvol),
            'open_interest': 70.0,  # TODO: Calculate from API
            'trend': self.scorer.calculate_trend_score(is_bullish, sum(a['trend_strength'] for a in tf_analyses.values()) / len(tf_analyses)),
            'market_structure': self.scorer.calculate_structure_score(list(tf_analyses.values())[0]['structure'], is_bullish),
            'breakout_strength': self.scorer.calculate_breakout_score(max(a['trend_strength'] for a in tf_analyses.values())),
            'multi_tf_alignment': self.scorer.calculate_multi_tf_score(aligned, len(tf_analyses)),
        }
        
        return scores
    
    def _is_on_cooldown(self, inst_id: str, action: str) -> bool:
        """Check if signal is on cooldown.
        
        Args:
            inst_id: Instrument ID
            action: Signal action
            
        Returns:
            True if on cooldown
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=settings.COOLDOWN_HOURS)
        last_signal = self.db.get_last_signal(inst_id, action)
        
        if last_signal and last_signal[8] > cutoff_time.isoformat():
            return True
        
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
        
        # Volume reason
        avg_rvol = sum(a['rvol'] for a in tf_analyses.values()) / len(tf_analyses)
        if avg_rvol >= settings.VERY_HIGH_RVOL:
            reasons.append(f"RVOL {avg_rvol:.1f}x above average")
        elif avg_rvol >= settings.HIGH_RVOL:
            reasons.append(f"RVOL {avg_rvol:.1f}x above average")
        
        # Trend reason
        if scores['trend'] >= 80:
            reasons.append("Strong trend confirmation")
        
        # Structure reason
        structure = list(tf_analyses.values())[0]['structure']
        if structure == 'bullish':
            reasons.append("Bullish breakout confirmed")
        elif structure == 'bearish':
            reasons.append("Bearish breakdown confirmed")
        
        # Multi-TF reason
        if scores['multi_tf_alignment'] >= 80:
            reasons.append("Multi-timeframe alignment bullish")
        
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
                return "Current market structure favors upside continuation."
            else:
                return "Bullish momentum detected across multiple timeframes."
        else:
            if structure == 'bearish':
                return "Bearish participation remains dominant and downside continuation is more likely."
            else:
                return "Bearish momentum detected across multiple timeframes."
