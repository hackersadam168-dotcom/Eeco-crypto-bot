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
    
    # ============================================
    # BINANCE API (No Authentication needed)
    # ============================================
    EXCHANGE = 'BINANCE'  # Using Binance (Works 100% in India)
    BINANCE_API_URL = 'https://fapi.binance.com/fapi/v1'
    
    # Telegram Configuration (Optional)
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # ============================================
    # BOT CONFIGURATION (Per Specification)
    # ============================================
    SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 3600))  # 1 hour (mandatory)
    CONFIDENCE_THRESHOLD = int(os.getenv('CONFIDENCE_THRESHOLD', 88))  # Minimum 88%
    COOLDOWN_HOURS = int(os.getenv('COOLDOWN_HOURS', 6))  # 6 hours cooldown
    
    # ============================================
    # TIMEFRAMES (Per Specification)
    # ============================================
    # Intraday: 15m, 1H
    INTRADAY_TIMEFRAMES = [15, 60]  # in minutes
    INTRADAY_INTERVALS = ['15m', '1h']  # Binance format
    
    # Swing: 4H, 1D
    SWING_TIMEFRAMES = [240, 1440]  # in minutes
    SWING_INTERVALS = ['4h', '1d']  # Binance format
    
    ALL_TIMEFRAMES = INTRADAY_TIMEFRAMES + SWING_TIMEFRAMES
    ALL_INTERVALS = INTRADAY_INTERVALS + SWING_INTERVALS
    
    # ============================================
    # DATABASE
    # ============================================
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/signals.db')
    
    # ============================================
    # LOGGING
    # ============================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = BASE_DIR / 'logs' / 'bot.log'
    
    # ============================================
    # ANALYSIS PARAMETERS
    # ============================================
    MIN_RVOL = 1.5
    HIGH_RVOL = 3.0
    VERY_HIGH_RVOL = 5.0
    
    # ============================================
    # CONFIDENCE WEIGHTS (Per Specification)
    # ============================================
    CONFIDENCE_WEIGHTS = {
        'price_expansion': 0.15,      # Price Expansion
        'relative_volume': 0.20,       # Relative Volume (RVOL)
        'spike': 0.10,                 # Spike Detection
        'open_interest': 0.15,         # Open Interest
        'trend': 0.15,                 # Trend Direction
        'market_structure': 0.15,      # Market Structure
        'breakout_strength': 0.10,     # Breakout Strength
    }
    
    # ============================================
    # RISK THRESHOLDS (Per Specification)
    # ============================================
    RISK_THRESHOLDS = {
        'low': {'volatility_max': 0.02, 'oi_change_min': 0.10},
        'medium': {'volatility_max': 0.05, 'oi_change_min': 0.05},
        'high': {'volatility_max': float('inf'), 'oi_change_min': 0.0},
    }
    
    # ============================================
    # FEATURE FLAGS (Per Specification)
    # ============================================
    ENABLE_SCALPING = False  # MUST BE FALSE - Hourly scans only
    ENABLE_AUTO_TRADING = False  # MUST BE FALSE - User decides
    ENABLE_HOLD_ALERTS = False  # MUST BE FALSE - Only BUY/SELL
    ENABLE_TELEGRAM = bool(TELEGRAM_BOT_TOKEN)  # Optional
    
    # ============================================
    # BOT RESTRICTIONS
    # ============================================
    ONLY_BUY_LONG = False  # Allow both BUY and SELL
    ONLY_SELL_SHORT = False  # Allow both BUY and SELL
    
    # Max pairs to scan per cycle
    MAX_PAIRS_SCAN = 100
    
    # Min candles for analysis
    MIN_CANDLES = 50

settings = Settings()
