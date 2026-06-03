"""Application settings and configuration."""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings:
    """Global application settings."""
    
    # Project root
    BASE_DIR = Path(__file__).parent.parent
    
    # Environment
    ENV = os.getenv('ENV', 'development')
    
    # OKX API Configuration
    OKX_API_KEY = os.getenv('OKX_API_KEY', '')
    OKX_API_SECRET = os.getenv('OKX_API_SECRET', '')
    OKX_API_PASSPHRASE = os.getenv('OKX_API_PASSPHRASE', '')
    OKX_API_URL = 'https://www.okx.com/api/v5'
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Bot Configuration
    SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 3600))  # 1 hour
    CONFIDENCE_THRESHOLD = int(os.getenv('CONFIDENCE_THRESHOLD', 75))  # Lowered from 88 to 75 for better signal generation
    COOLDOWN_HOURS = int(os.getenv('COOLDOWN_HOURS', 6))
    
    # Timeframes (in minutes)
    INTRADAY_TIMEFRAMES = [15, 60]  # 15m, 1H
    SWING_TIMEFRAMES = [240, 1440]  # 4H, 1D
    ALL_TIMEFRAMES = INTRADAY_TIMEFRAMES + SWING_TIMEFRAMES
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/signals.db')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = BASE_DIR / 'logs' / 'bot.log'
    
    # Analysis parameters
    MIN_RVOL = 1.5
    HIGH_RVOL = 3.0
    VERY_HIGH_RVOL = 5.0
    
    # Confidence weights
    CONFIDENCE_WEIGHTS = {
        'price_expansion': 0.15,
        'relative_volume': 0.20,
        'open_interest': 0.15,
        'trend': 0.15,
        'market_structure': 0.15,
        'breakout_strength': 0.10,
        'multi_tf_alignment': 0.10,
    }
    
    # Risk thresholds
    RISK_THRESHOLDS = {
        'low': {'volatility_max': 0.02, 'oi_change_min': 0.10},
        'medium': {'volatility_max': 0.05, 'oi_change_min': 0.05},
        'high': {'volatility_max': float('inf'), 'oi_change_min': 0.0},
    }

settings = Settings()
