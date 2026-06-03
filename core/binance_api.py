"""Binance API client for fetching market data - No authentication required."""
import requests
import time
from typing import Dict, List, Optional, Any
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class BinanceAPIClient:
    """Client for interacting with Binance Public API (No Auth needed for India)."""
    
    def __init__(self):
        """Initialize Binance API client."""
        self.base_url = 'https://fapi.binance.com/fapi/v1'
        self.public_url = 'https://fapi.binance.com'
        self.session = requests.Session()
        self.timeout = 15
        self.request_count = 0
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting to avoid 429 errors."""
        elapsed = time.time() - self.last_request_time
        if elapsed < 0.2:  # 200ms between requests
            time.sleep(0.2 - elapsed)
        self.last_request_time = time.time()
    
    def _request(self, endpoint: str, params: Dict = None, retries: int = 3) -> Optional[Dict]:
        """Make API request with retry logic.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            retries: Number of retry attempts
            
        Returns:
            Response data or None
        """
        for attempt in range(retries):
            try:
                self._rate_limit()
                url = f'{self.base_url}{endpoint}'
                response = self.session.get(url, params=params, timeout=self.timeout)
                
                if response.status_code == 429:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.debug(f"Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.debug(f"Timeout (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            except requests.exceptions.ConnectionError:
                logger.debug(f"Connection Error (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            except Exception as e:
                logger.debug(f"API Request Error: {str(e)}")
                return None
        
        return None
    
    def get_all_futures_symbols(self) -> List[str]:
        """Get all USDT futures trading pairs.
        
        Returns:
            List of symbol IDs (e.g., 'BTCUSDT')
        """
        try:
            endpoint = '/exchangeInfo'
            data = self._request(endpoint)
            
            if not data or 'symbols' not in data:
                logger.warning("No exchange info data returned")
                return []
            
            # Filter for USDT futures that are trading
            usdt_symbols = [
                symbol['symbol'] for symbol in data['symbols']
                if symbol['symbol'].endswith('USDT') and symbol['status'] == 'TRADING'
            ]
            
            logger.info(f"Found {len(usdt_symbols)} USDT futures pairs on Binance")
            
            # Return top 100 active pairs
            return sorted(usdt_symbols)[:100]
        except Exception as e:
            logger.error(f"Error fetching symbols: {str(e)}")
            return []
    
    def get_candles(self, symbol: str, interval: str, limit: int = 100) -> Optional[List[Dict]]:
        """Fetch candlestick data.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to fetch (max 1500)
            
        Returns:
            List of candle data or None
        """
        try:
            endpoint = '/klines'
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': min(limit, 1500),
            }
            
            data = self._request(endpoint, params)
            if not data:
                return None
            
            # Convert to standard format
            candles = []
            for candle in data:
                candles.append({
                    'timestamp': int(candle[0]),
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'volume': float(candle[7]),  # Quote asset volume for consistency
                })
            
            return candles
        except Exception as e:
            logger.debug(f"Error fetching candles for {symbol}: {str(e)}")
            return None
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Get current ticker data.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Ticker data or None
        """
        try:
            endpoint = '/ticker/24hr'
            params = {'symbol': symbol}
            
            data = self._request(endpoint, params)
            if data:
                return {
                    'lastPrice': float(data.get('lastPrice', 0)),
                    'priceChangePercent': float(data.get('priceChangePercent', 0)),
                    'volume': float(data.get('quoteAssetVolume', 0)),
                    'high24h': float(data.get('highPrice', 0)),
                    'low24h': float(data.get('lowPrice', 0)),
                }
            return None
        except Exception as e:
            logger.debug(f"Error fetching ticker for {symbol}: {str(e)}")
            return None
    
    def get_open_interest(self, symbol: str) -> Optional[float]:
        """Get open interest data.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Open interest or None
        """
        try:
            endpoint = '/openInterest'
            params = {'symbol': symbol}
            
            data = self._request(endpoint, params)
            if data and 'openInterest' in data:
                return float(data['openInterest'])
            return None
        except Exception as e:
            logger.debug(f"Error fetching OI for {symbol}: {str(e)}")
            return None
    
    def get_funding_rate(self, symbol: str) -> Optional[float]:
        """Get current funding rate.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Funding rate or None
        """
        try:
            endpoint = '/fundingRate'
            params = {
                'symbol': symbol,
                'limit': 1
            }
            
            data = self._request(endpoint, params)
            if data and len(data) > 0:
                return float(data[0].get('fundingRate', 0))
            return None
        except Exception as e:
            logger.debug(f"Error fetching funding rate for {symbol}: {str(e)}")
            return None
