"""OKX API client for fetching market data."""
import requests
import hmac
import hashlib
import base64
import time
from typing import Dict, List, Optional, Any
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class OKXAPIClient:
    """Client for interacting with OKX API."""
    
    def __init__(self, api_key: str = None, api_secret: str = None, passphrase: str = None):
        """Initialize OKX API client.
        
        Args:
            api_key: OKX API key
            api_secret: OKX API secret
            passphrase: OKX API passphrase
        """
        self.api_key = api_key or settings.OKX_API_KEY
        self.api_secret = api_secret or settings.OKX_API_SECRET
        self.passphrase = passphrase or settings.OKX_API_PASSPHRASE
        self.base_url = settings.OKX_API_URL
        self.session = requests.Session()
    
    def _get_timestamp(self) -> str:
        """Get current UTC timestamp in ISO format."""
        return time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
    
    def _sign_request(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        """Generate signature for API request.
        
        Args:
            timestamp: Request timestamp
            method: HTTP method
            request_path: API endpoint path
            body: Request body
            
        Returns:
            Base64 encoded signature
        """
        message = timestamp + method + request_path + body
        mac = hmac.new(
            bytes(self.api_secret, encoding='utf8'),
            bytes(message, encoding='utf8'),
            digestmod=hashlib.sha256
        )
        d = mac.digest()
        return base64.b64encode(d).decode('utf-8')
    
    def _request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """Make API request with authentication.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body
            
        Returns:
            Response data
        """
        try:
            timestamp = self._get_timestamp()
            request_path = f'/api/v5{endpoint}'
            body = ''
            
            headers = {
                'OK-ACCESS-KEY': self.api_key,
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-SIGN': self._sign_request(timestamp, method, request_path, body),
                'OK-ACCESS-PASSPHRASE': self.passphrase,
                'Content-Type': 'application/json',
            }
            
            url = f'{self.base_url}{endpoint}'
            response = self.session.request(method, url, params=params, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') != '0':
                logger.error(f"API Error: {result.get('msg')}")
                return None
            
            return result.get('data', [])
        except Exception as e:
            logger.error(f"API Request Error: {str(e)}")
            return None
    
    def get_public(self, endpoint: str, params: Dict = None) -> Dict:
        """Make public API request (no authentication).
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response data
        """
        try:
            url = f'{self.base_url}{endpoint}'
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') != '0':
                logger.error(f"API Error: {result.get('msg')}")
                return None
            
            return result.get('data', [])
        except Exception as e:
            logger.error(f"Public API Request Error: {str(e)}")
            return None
    
    def get_all_swap_instruments(self) -> List[str]:
        """Get all USDT perpetual swap pairs.
        
        Returns:
            List of instrument IDs (e.g., 'BTC-USDT-SWAP')
        """
        try:
            endpoint = '/public/instruments'
            params = {
                'instType': 'SWAP',
                'state': 'live',
            }
            
            data = self.get_public(endpoint, params)
            if not data:
                return []
            
            # Filter for USDT pairs only
            usdt_pairs = [
                inst['instId'] for inst in data
                if inst['instId'].endswith('-USDT-SWAP')
            ]
            
            logger.info(f"Found {len(usdt_pairs)} USDT perpetual pairs")
            return usdt_pairs
        except Exception as e:
            logger.error(f"Error fetching instruments: {str(e)}")
            return []
    
    def get_candles(self, inst_id: str, timeframe: int, limit: int = 100) -> List[Dict]:
        """Fetch candle data.
        
        Args:
            inst_id: Instrument ID
            timeframe: Timeframe in minutes (15, 60, 240, 1440)
            limit: Number of candles to fetch
            
        Returns:
            List of candle data
        """
        try:
            # Convert minutes to OKX format
            tf_map = {
                15: '15m',
                60: '1H',
                240: '4H',
                1440: '1D',
            }
            
            bar = tf_map.get(timeframe)
            if not bar:
                logger.error(f"Unsupported timeframe: {timeframe}")
                return []
            
            endpoint = '/market/candles'
            params = {
                'instId': inst_id,
                'bar': bar,
                'limit': min(limit, 100),  # Max 100 per request
            }
            
            data = self.get_public(endpoint, params)
            if not data:
                return []
            
            # Sort by timestamp ascending
            return sorted(data, key=lambda x: int(x[0]))
        except Exception as e:
            logger.error(f"Error fetching candles for {inst_id}: {str(e)}")
            return []
    
    def get_ticker(self, inst_id: str) -> Optional[Dict]:
        """Get current ticker data.
        
        Args:
            inst_id: Instrument ID
            
        Returns:
            Ticker data
        """
        try:
            endpoint = '/market/ticker'
            params = {'instId': inst_id}
            
            data = self.get_public(endpoint, params)
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Error fetching ticker for {inst_id}: {str(e)}")
            return None
    
    def get_open_interest(self, inst_id: str) -> Optional[Dict]:
        """Get open interest data.
        
        Args:
            inst_id: Instrument ID
            
        Returns:
            Open interest data
        """
        try:
            endpoint = '/public/open-interest'
            params = {'instId': inst_id}
            
            data = self.get_public(endpoint, params)
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Error fetching OI for {inst_id}: {str(e)}")
            return None
    
    def get_funding_rate(self, inst_id: str) -> Optional[Dict]:
        """Get funding rate data.
        
        Args:
            inst_id: Instrument ID
            
        Returns:
            Funding rate data
        """
        try:
            endpoint = '/public/funding-rate'
            params = {'instId': inst_id}
            
            data = self.get_public(endpoint, params)
            return data[0] if data else None
        except Exception as e:
            logger.error(f"Error fetching funding rate for {inst_id}: {str(e)}")
            return None
