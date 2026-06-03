#!/usr/bin/env python3
"""Main bot entry point - Production ready for Binance (India-compatible)."""
import sys
import time
import signal
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR
from core.binance_api import BinanceAPIClient
from core.signal_engine import SignalEngine
from database.db_manager import DatabaseManager
from telegram.notifier import TelegramNotifier
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class CryptoFuturesBotManager:
    """Main bot manager - Using Binance API (Works 100% in India)."""
    
    def __init__(self):
        """Initialize bot manager."""
        try:
            logger.info("="*70)
            logger.info("CRYPTO FUTURES MARKET INTELLIGENCE BOT - BINANCE")
            logger.info("="*70)
            logger.info(f"Exchange: {settings.EXCHANGE}")
            logger.info(f"Region: India (100% Compatible)")
            logger.info(f"Auth: Public API Only (No credentials needed)")
            logger.info("="*70)
            
            # Initialize components
            self.api_client = BinanceAPIClient()
            self.db_manager = DatabaseManager()
            self.signal_engine = SignalEngine(self.api_client, self.db_manager)
            self.telegram = TelegramNotifier()
            self.last_scan_time = None
            self.scheduler = None
            
            # Test API connection
            logger.info("\n🔍 Testing Binance API connection...")
            test_symbols = self.api_client.get_all_futures_symbols()
            if test_symbols:
                logger.info(f"✅ Successfully connected to Binance!")
                logger.info(f"✅ Found {len(test_symbols)} USDT futures pairs")
            else:
                logger.warning("⚠️ Could not fetch symbols from Binance")
            
            logger.info("\n📊 Bot Configuration:")
            logger.info(f"   Confidence Threshold: {settings.CONFIDENCE_THRESHOLD}%")
            logger.info(f"   Scan Interval: {settings.SCAN_INTERVAL}s (1 hour)")
            logger.info(f"   Cooldown: {settings.COOLDOWN_HOURS}h per coin")
            logger.info(f"   Timeframes: 15m, 1H (Intraday) | 4H, 1D (Swing)")
            logger.info(f"   Max Pairs: {settings.MAX_PAIRS_SCAN}")
            logger.info(f"   Telegram: {'✅ Enabled' if settings.ENABLE_TELEGRAM else '❌ Disabled'}")
            
            logger.info("\n✅ Bot initialized successfully!")
            logger.info("="*70 + "\n")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {str(e)}")
            raise
    
    def run_scan(self):
        """Run a complete market scan."""
        scan_start = datetime.utcnow()
        
        try:
            logger.info("="*70)
            logger.info(f"⏱️  MARKET SCAN STARTED - {scan_start.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            logger.info("="*70)
            
            # Get all USDT futures pairs
            pairs = self.api_client.get_all_futures_symbols()
            if not pairs:
                logger.warning("⚠️  No pairs found from Binance")
                return
            
            logger.info(f"📊 Scanning {len(pairs)} pairs across timeframes...")
            signals_generated = 0
            buy_signals = 0
            sell_signals = 0
            errors = 0
            
            # Analyze each pair
            for idx, pair in enumerate(pairs, 1):
                try:
                    if idx % 10 == 0:
                        logger.debug(f"   Progress: {idx}/{len(pairs)}")
                    
                    signal = self.signal_engine.analyze_pair(pair)
                    
                    if signal:
                        # Store in database
                        self.db_manager.insert_signal(signal)
                        
                        # Send to Telegram if enabled
                        if settings.ENABLE_TELEGRAM:
                            success = self.telegram.send_signal_alert(signal)
                            if not success:
                                logger.warning(f"⚠️  Failed to send Telegram alert for {pair}")
                        
                        signals_generated += 1
                        if signal['action'] == 'BUY LONG':
                            buy_signals += 1
                            logger.info(f"✅ BUY LONG: {pair} | Confidence: {signal['confidence']}% | Risk: {signal['risk']}")
                        else:
                            sell_signals += 1
                            logger.info(f"✅ SELL SHORT: {pair} | Confidence: {signal['confidence']}% | Risk: {signal['risk']}")
                    
                    # Rate limiting
                    time.sleep(0.05)
                except Exception as e:
                    errors += 1
                    logger.debug(f"Error analyzing {pair}: {str(e)}")
                    continue
            
            # Update last scan time
            self.last_scan_time = datetime.utcnow()
            scan_duration = (datetime.utcnow() - scan_start).total_seconds()
            
            # Log scan completion
            logger.info("\n" + "="*70)
            logger.info("📊 SCAN COMPLETED")
            logger.info("="*70)
            logger.info(f"⏱️  Duration: {scan_duration:.2f}s")
            logger.info(f"📈 Signals Generated: {signals_generated}")
            logger.info(f"  ├─ BUY LONG: {buy_signals}")
            logger.info(f"  └─ SELL SHORT: {sell_signals}")
            logger.info(f"⚠️  Errors: {errors}")
            logger.info(f"⏰ Next scan: In {settings.SCAN_INTERVAL}s")
            logger.info("="*70 + "\n")
            
        except Exception as e:
            logger.error(f"❌ Error during market scan: {str(e)}")
            if settings.ENABLE_TELEGRAM:
                self.telegram.send_message(f"⚠️ Bot Error: {str(e)}")
    
    def job_error_listener(self, event):
        """Handle job errors."""
        if event.exception:
            logger.error(f"❌ Job error: {str(event.exception)}")
            if settings.ENABLE_TELEGRAM:
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
                name='Binance Market Scan',
                max_instances=1,
            )
            
            # Run first scan immediately
            logger.info("🚀 Running initial scan...\n")
            self.run_scan()
            
            logger.info(f"✅ Scheduler started successfully!")
            logger.info(f"⏰ Next scan in {settings.SCAN_INTERVAL}s\n")
            logger.info("Bot is running and monitoring the market... 🤖\n")
            
            self.scheduler.start()
        except KeyboardInterrupt:
            logger.info("⏹️  Bot stopped by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"❌ Scheduler error: {str(e)}")
            raise
    
    def shutdown(self):
        """Graceful shutdown."""
        try:
            logger.info("🛑 Shutting down bot...")
            if self.scheduler:
                self.scheduler.shutdown()
            logger.info("✅ Bot stopped successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info(f"\n⏹️  Received signal {sig}. Shutting down...")
    sys.exit(0)

def main():
    """Main entry point."""
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start bot
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
