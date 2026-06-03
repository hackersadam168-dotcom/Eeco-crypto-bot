"""Database manager for storing signals and history."""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    """Manage SQLite database for signal storage."""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path or settings.DATABASE_PATH
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist."""
        try:
            # Create directory if needed
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin TEXT NOT NULL,
                    action TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    risk TEXT NOT NULL,
                    reason TEXT,
                    bot_view TEXT,
                    price REAL NOT NULL,
                    timeframe TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for quick lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_coin_action_timestamp
                ON signals(coin, action, timestamp)
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
    
    def insert_signal(self, signal: dict) -> bool:
        """Insert a signal into the database.
        
        Args:
            signal: Signal dict
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO signals 
                (coin, action, signal_type, confidence, risk, reason, bot_view, price, timeframe, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.get('coin'),
                signal.get('action'),
                signal.get('type'),
                signal.get('confidence'),
                signal.get('risk'),
                '\n'.join(signal.get('reason', [])),
                signal.get('bot_view'),
                signal.get('price'),
                signal.get('timeframe_group'),
                signal.get('timestamp'),
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Signal stored for {signal.get('coin')}")
            return True
        except Exception as e:
            logger.error(f"Error inserting signal: {str(e)}")
            return False
    
    def get_last_signal(self, coin: str, action: str) -> Optional[Tuple]:
        """Get last signal for a coin and action.
        
        Args:
            coin: Coin symbol
            action: Signal action (BUY LONG or SELL SHORT)
            
        Returns:
            Signal tuple or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM signals
                WHERE coin = ? AND action = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (coin, action))
            
            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Error fetching last signal: {str(e)}")
            return None
    
    def get_signals_today(self) -> List[Tuple]:
        """Get all signals from today.
        
        Returns:
            List of signal tuples
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.utcnow().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT * FROM signals
                WHERE DATE(timestamp) = ?
                ORDER BY timestamp DESC
            ''', (today,))
            
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error fetching today's signals: {str(e)}")
            return []
    
    def get_signal_count_today(self) -> Tuple[int, int, int]:
        """Get today's signal count summary.
        
        Returns:
            (total, buy_long, sell_short)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.utcnow().strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT COUNT(*) FROM signals
                WHERE DATE(timestamp) = ?
            ''', (today,))
            total = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM signals
                WHERE DATE(timestamp) = ? AND action = 'BUY LONG'
            ''', (today,))
            buy_long = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM signals
                WHERE DATE(timestamp) = ? AND action = 'SELL SHORT'
            ''', (today,))
            sell_short = cursor.fetchone()[0]
            
            conn.close()
            return (total, buy_long, sell_short)
        except Exception as e:
            logger.error(f"Error fetching signal count: {str(e)}")
            return (0, 0, 0)
    
    def get_top_opportunities(self, limit: int = 5) -> List[Tuple]:
        """Get top signals by confidence today.
        
        Args:
            limit: Number of results
            
        Returns:
            List of signal tuples
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.utcnow().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT * FROM signals
                WHERE DATE(timestamp) = ?
                ORDER BY confidence DESC
                LIMIT ?
            ''', (today, limit))
            
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error fetching top opportunities: {str(e)}")
            return []
