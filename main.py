#!/usr/bin/env python3
"""Main bot entry point - Production ready."""
import sys
import time
import signal
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR
from core.okx_api import OKXAPIClient
from core.signal_engine import SignalEngine
from database.db_manager import DatabaseManager
from telegram.notifier import TelegramNotifier
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class CryptoFuturesBotManager:
    """Main bot manager - Production version."""
    
    def __init__(self):
        """Initialize bot manager."""
        try:
            # Validate configuration
            if not settings.OKX_API_KEY or not settings.OKX_API_SECRET:
                logger.warning("⚠️ WARNING: OKX API credentials not set! Using public endpoints only.")
            if not settings.TELEGRAM_BOT_TOKEN:
                logger.warning("⚠️ WARNING: Telegram bot token not set! Signals won't be sent.")
            
            self.api_client = OKXAPIClient()
            self.db_manager = DatabaseManager()
            self.signal_engine = SignalEngine(self.db_manager)
            self.telegram = TelegramNotifier()
            self.last_scan_time = None
            self.scheduler = None
            
            logger.info("Bot initialized successfully")
            logger.info(f"Confidence Threshold: {settings.CONFIDENCE_THRESHOLD}")
            logger.info(f"Scan Interval: {settings.SCAN_INTERVAL}s")
            logger.info(f"Cooldown: {settings.COOLDOWN_HOURS}h")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {str(e)}")
            raise
    
    def run_scan(self):
        """Run a complete market scan."""
        scan_start = datetime.utcnow()
        
        try:
            logger.info("="*60)
            logger.info("Starting market scan...")
            
            # Get all USDT swap pairs
            pairs = self.api_client.get_all_swap_instruments()
            if not pairs:
                logger.warning("No pairs found")
                return
            
            logger.info(f"Scanning {len(pairs)} pairs")
            signals_generated = 0
            buy_signals = 0
            sell_signals = 0
            
            # Analyze each pair
            for idx, pair in enumerate(pairs, 1):
                try:
                    logger.debug(f"Analyzing {pair} ({idx}/{len(pairs)})")
                    signal = self.signal_engine.analyze_pair(pair)
                    
                    if signal:
                        # Store in database
                        self.db_manager.insert_signal(signal)
                        
                        # Send to Telegram
                        success = self.telegram.send_signal_alert(signal)
                        
                        if success:
                            signals_generated += 1
                            if signal['action'] == 'BUY LONG':
                                buy_signals += 1
                            else:
                                sell_signals += 1
                            logger.info(f"✅ SIGNAL: {pair} {signal['action']} (Confidence: {signal['confidence']}%)")
                    
                    # Rate limiting - respect API limits
                    time.sleep(0.05)
                except Exception as e:
                    logger.debug(f"Error analyzing {pair}: {str(e)}")
                    continue
            
            # Update last scan time
            self.last_scan_time = datetime.utcnow()
            scan_duration = (datetime.utcnow() - scan_start).total_seconds()
            
            # Log scan completion
            logger.info(f"\nScan completed in {scan_duration:.2f}s")
            logger.info(f"Signals Generated: {signals_generated}")
            logger.info(f"  └─ BUY LONG: {buy_signals}")
            logger.info(f"  └─ SELL SHORT: {sell_signals}")
            logger.info("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"Error during market scan: {str(e)}")
            self.telegram.send_message(f"⚠️ Bot Error: {str(e)}")
    
    def job_error_listener(self, event):
        """Handle job errors."""
        if event.exception:
            logger.error(f"Job error: {str(event.exception)}")
            self.telegram.send_message(f"🚨 Job Error: {str(event.exception)}")
    
    def start_scheduler(self):
        """Start the scan scheduler."""
        try:
            self.scheduler = BlockingScheduler()
            
            # Add error listener
            self.scheduler.add_listener(self.job_error_listener, EVENT_JOB_ERROR)
            
            # Schedule scan
            self.scheduler.add_job(
                self.run_scan,
                'interval',
                seconds=settings.SCAN_INTERVAL,
                id='market_scan',
                name='Market Scan Job',
                max_instances=1,  # Prevent concurrent execution
            )
            
            # Run first scan immediately
            logger.info("\nRunning initial scan...")
            self.run_scan()
            
            logger.info(f"Scheduler started. Next scan in {settings.SCAN_INTERVAL}s ({settings.SCAN_INTERVAL/3600:.1f}h)\n")
            self.scheduler.start()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            raise
    
    def shutdown(self):
        """Graceful shutdown."""
        try:
            logger.info("Shutting down bot...")
            if self.scheduler:
                self.scheduler.shutdown()
            logger.info("Bot stopped")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info(f"\nReceived signal {sig}. Shutting down...")
    sys.exit(0)

def main():
    """Main entry point."""
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("\n" + "="*60)
        logger.info("CRYPTO FUTURES BOT - PRODUCTION")
        logger.info("="*60)
        logger.info(f"Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.info(f"Environment: {settings.ENV}")
        logger.info("="*60 + "\n")
        
        bot = CryptoFuturesBotManager()
        bot.start_scheduler()
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
