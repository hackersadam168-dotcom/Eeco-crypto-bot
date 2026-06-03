"""CoinGecko API client - Free, No API Key Needed."""
import requests
import time
from typing import Dict, List, Optional
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class CoinGeckoClient:
    """Client for CoinGecko free API - No authentication needed."""
    
    def __init__(self):
        """Initialize CoinGecko API client."""
        self.base_url = 'https://api.coingecko.com/api/v3'
        self.session = requests.Session()
        self.timeout = 15
    
    def test_connection(self) -> bool:
        """Test API connection.
        
        Returns:
            True if connection works
        """
        try:
            url = f"{self.base_url}/ping"
            response = requests.get(url, timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def _get(self, endpoint: str, params: Dict = None, retries: int = 3) -> Optional[Dict]:
        """Make GET request to CoinGecko API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            retries: Number of retry attempts
            
        Returns:
            Response data or None
        """
        for attempt in range(retries):
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                logger.warning(f"API Timeout (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            except Exception as e:
                logger.error(f"API Error: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        return None
    
    def get_top_cryptocurrencies(self, limit: int = 100) -> List[Dict]:
        """Get top cryptocurrencies by market cap.
        
        Args:
            limit: Number of cryptos to fetch (max 250)
            
        Returns:
            List of cryptocurrency data
        """
        try:
            endpoint = '/markets'
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': min(limit, 250),
                'page': 1,
                'sparkline': False,
            }
            
            data = self._get(endpoint, params)
            return data if data else []
        except Exception as e:
            logger.error(f"Error fetching cryptocurrencies: {str(e)}")
            return []
    
    def get_crypto_price(self, crypto_id: str, vs_currency: str = 'usd') -> Optional[Dict]:
        """Get current price of a cryptocurrency.
        
        Args:
            crypto_id: Cryptocurrency ID (e.g., 'bitcoin')
            vs_currency: Target currency (default 'usd')
            
        Returns:
            Price data or None
        """
        try:
            endpoint = f'/simple/price'
            params = {
                'ids': crypto_id,
                'vs_currencies': vs_currency,
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true',
            }
            
            data = self._get(endpoint, params)
            return data.get(crypto_id) if data else None
        except Exception as e:
            logger.error(f"Error fetching price for {crypto_id}: {str(e)}")
            return None
    
    def get_ohlcv_data(self, crypto_id: str, days: int = 30, vs_currency: str = 'usd') -> Optional[List]:
        """Get OHLCV historical data.
        
        Args:
            crypto_id: Cryptocurrency ID
            days: Number of days (1-365)
            vs_currency: Target currency
            
        Returns:
            List of [timestamp, open, high, low, close] or None
        """
        try:
            endpoint = f'/coins/{crypto_id}/ohlc'
            params = {
                'vs_currency': vs_currency,
                'days': min(max(days, 1), 365),
            }
            
            data = self._get(endpoint, params)
            return data if data else None
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {crypto_id}: {str(e)}")
            return None
    
    def get_market_data(self, crypto_id: str) -> Optional[Dict]:
        """Get detailed market data.
        
        Args:
            crypto_id: Cryptocurrency ID
            
        Returns:
            Market data or None
        """
        try:
            endpoint = f'/coins/{crypto_id}'
            params = {
                'localization': False,
                'tickers': False,
                'market_data': True,
                'community_data': False,
                'developer_data': False,
            }
            
            data = self._get(endpoint, params)
            if data and 'market_data' in data:
                return data['market_data']
            return None
        except Exception as e:
            logger.error(f"Error fetching market data for {crypto_id}: {str(e)}")
            return None
    
    def search_crypto(self, query: str) -> Optional[List]:
        """Search for cryptocurrencies.
        
        Args:
            query: Search query
            
        Returns:
            List of matching cryptocurrencies or None
        """
        try:
            endpoint = '/search'
            params = {'query': query}
            
            data = self._get(endpoint, params)
            return data.get('coins', []) if data else None
        except Exception as e:
            logger.error(f"Error searching for {query}: {str(e)}")
            return None
    
    def get_all_supported_coins(self) -> List[Dict]:
        """Get all supported cryptocurrencies.
        
        Returns:
            List of all supported coins
        """
        try:
            endpoint = '/coins/list'
            params = {'include_platform': False}
            
            data = self._get(endpoint, params)
            return data if data else []
        except Exception as e:
            logger.error(f"Error fetching supported coins: {str(e)}")
            return []
    
    def get_trending_cryptos(self) -> Optional[List]:
        """Get trending cryptocurrencies.
        
        Returns:
            List of trending cryptos or None
        """
        try:
            endpoint = '/search/trending'
            data = self._get(endpoint)
            return data.get('coins', []) if data else None
        except Exception as e:
            logger.error(f"Error fetching trending cryptos: {str(e)}")
            return None
    
    def get_crypto_list_with_volumes(self) -> List[Dict]:
        """Get list of cryptos sorted by volume.
        
        Returns:
            List of cryptos with volume data
        """
        try:
            endpoint = '/markets'
            params = {
                'vs_currency': 'usd',
                'order': 'volume_desc',
                'per_page': 100,
                'page': 1,
                'sparkline': False,
            }
            
            data = self._get(endpoint, params)
            return data if data else []
        except Exception as e:
            logger.error(f"Error fetching volume list: {str(e)}")
            return []
