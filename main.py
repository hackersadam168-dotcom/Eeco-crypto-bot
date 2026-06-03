#!/usr/bin/env python3
"""Main bot entry point."""
import sys
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from core.okx_api import OKXAPIClient
from core.signal_engine import SignalEngine
from database.db_manager import DatabaseManager
from telegram.notifier import TelegramNotifier
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class CryptoFuturesBotManager:
    """Main bot manager."""
    
    def __init__(self):
        """Initialize bot manager."""
        self.api_client = OKXAPIClient()
        self.db_manager = DatabaseManager()
        self.signal_engine = SignalEngine(self.db_manager)
        self.telegram = TelegramNotifier()
        self.last_scan_time = None
        
        logger.info("Bot initialized successfully")
    
    def run_scan(self):
        """Run a complete market scan."""
        try:
            logger.info("Starting market scan...")
            scan_start = datetime.utcnow()
            
            # Get all USDT swap pairs
            pairs = self.api_client.get_all_swap_instruments()
            if not pairs:
                logger.warning("No pairs found")
                return
            
            logger.info(f"Scanning {len(pairs)} pairs")
            
            signals_generated = 0
            
            # Analyze each pair
            for pair in pairs:
                try:
                    signal = self.signal_engine.analyze_pair(pair)
                    
                    if signal:
                        # Store in database
                        self.db_manager.insert_signal(signal)
                        
                        # Send to Telegram
                        self.telegram.send_signal_alert(signal)
                        
                        signals_generated += 1
                        logger.info(f"Signal generated for {pair}: {signal['action']}")
                    
                    # Rate limiting
                    time.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error analyzing {pair}: {str(e)}")
            
            # Update last scan time
            self.last_scan_time = datetime.utcnow()
            
            scan_duration = (datetime.utcnow() - scan_start).total_seconds()
            logger.info(f"Scan completed in {scan_duration:.2f}s. Signals: {signals_generated}")
            
        except Exception as e:
            logger.error(f"Error during market scan: {str(e)}")
    
    def start_scheduler(self):
        """Start the scan scheduler."""
        try:
            scheduler = BlockingScheduler()
            
            # Schedule scan every hour
            scheduler.add_job(
                self.run_scan,
                'interval',
                seconds=settings.SCAN_INTERVAL,
                id='market_scan',
                name='Market Scan Job'
            )
            
            # Run first scan immediately
            logger.info("Running initial scan...")
            self.run_scan()
            
            logger.info(f"Scheduler started. Next scan in {settings.SCAN_INTERVAL}s")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")

def main():
    """Main entry point."""
    try:
        logger.info("===" * 20)
        logger.info("CRYPTO FUTURES BOT STARTING")
        logger.info(f"Confidence Threshold: {settings.CONFIDENCE_THRESHOLD}")
        logger.info(f"Scan Interval: {settings.SCAN_INTERVAL}s ({settings.SCAN_INTERVAL/3600:.1f}h)")
        logger.info(f"Cooldown: {settings.COOLDOWN_HOURS}h")
        logger.info("===" * 20)
        
        bot = CryptoFuturesBotManager()
        bot.start_scheduler()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
