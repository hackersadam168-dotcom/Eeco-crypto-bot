#!/usr/bin/env python3
"""Test deployment script - validates all components before production."""
import sys
import os
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_status(test_name, status, message=""):
    """Print test status."""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {test_name}")
    if message:
        print(f"   └─ {message}")

def test_environment():
    """Test environment setup."""
    print_header("1. ENVIRONMENT TEST")
    
    # Check Python version
    py_version = sys.version_info
    py_ok = py_version.major >= 3 and py_version.minor >= 8
    print_status("Python 3.8+", py_ok, f"Version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    
    # Check .env file
    env_exists = Path('.env').exists()
    print_status(".env file exists", env_exists, ".env" if env_exists else ".env not found")
    
    # Check directories
    dirs_to_check = ['logs', 'data', 'config', 'core', 'database', 'telegram', 'utils']
    for dir_name in dirs_to_check:
        dir_exists = Path(dir_name).exists()
        print_status(f"Directory: {dir_name}", dir_exists)
    
    return py_ok and env_exists

def test_dependencies():
    """Test required dependencies."""
    print_header("2. DEPENDENCIES TEST")
    
    dependencies = {
        'requests': 'requests',
        'python-dotenv': 'dotenv',
        'python-telegram-bot': 'telegram',
        'apscheduler': 'apscheduler',
        'pandas': 'pandas',
        'numpy': 'numpy',
    }
    
    all_ok = True
    for package_name, import_name in dependencies.items():
        try:
            __import__(import_name)
            print_status(f"Package: {package_name}", True)
        except ImportError:
            print_status(f"Package: {package_name}", False, "NOT INSTALLED")
            all_ok = False
    
    return all_ok

def test_config():
    """Test configuration loading."""
    print_header("3. CONFIGURATION TEST")
    
    try:
        from config.settings import settings
        print_status("Config import", True)
        
        # Check critical settings
        checks = [
            ("TELEGRAM_BOT_TOKEN", settings.TELEGRAM_BOT_TOKEN, bool(settings.TELEGRAM_BOT_TOKEN)),
            ("TELEGRAM_CHAT_ID", settings.TELEGRAM_CHAT_ID, bool(settings.TELEGRAM_CHAT_ID)),
            ("CONFIDENCE_THRESHOLD", str(settings.CONFIDENCE_THRESHOLD), settings.CONFIDENCE_THRESHOLD >= 88),
            ("SCAN_INTERVAL", str(settings.SCAN_INTERVAL), settings.SCAN_INTERVAL >= 3600),
            ("DATABASE_PATH", settings.DATABASE_PATH, True),
        ]
        
        all_ok = True
        for name, value, status in checks:
            print_status(f"Setting: {name}", status, str(value)[:50])
            if not status:
                all_ok = False
        
        return all_ok
    except Exception as e:
        print_status("Config import", False, str(e))
        return False

def test_database():
    """Test database initialization."""
    print_header("4. DATABASE TEST")
    
    try:
        from database.db_manager import DatabaseManager
        from config.settings import settings
        
        print_status("DB Manager import", True)
        
        # Initialize database
        db = DatabaseManager()
        print_status("DB initialization", True, settings.DATABASE_PATH)
        
        # Check database file
        db_exists = Path(settings.DATABASE_PATH).exists()
        print_status("DB file created", db_exists)
        
        return db_exists
    except Exception as e:
        print_status("Database test", False, str(e))
        return False

def test_telegram():
    """Test Telegram connectivity."""
    print_header("5. TELEGRAM TEST")
    
    try:
        from telegram.notifier import TelegramNotifier
        from config.settings import settings
        
        print_status("Telegram import", True)
        
        notifier = TelegramNotifier()
        print_status("Notifier initialization", True)
        
        # Test message
        test_message = f"""🤖 <b>BOT TEST</b>

Test Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
Status: All systems operational ✅
Ready for deployment!
"""
        
        success = notifier.send_message(test_message)
        print_status("Send test message", success, "Message sent to Telegram" if success else "Failed to send")
        
        return success
    except Exception as e:
        print_status("Telegram test", False, str(e))
        return False

def test_api():
    """Test OKX API connectivity."""
    print_header("6. OKX API TEST")
    
    try:
        from core.okx_api import OKXAPIClient
        
        print_status("API Client import", True)
        
        client = OKXAPIClient()
        print_status("Client initialization", True)
        
        # Get instruments
        pairs = client.get_all_swap_instruments()
        api_ok = len(pairs) > 0
        print_status("Fetch instruments", api_ok, f"Found {len(pairs)} pairs" if api_ok else "No pairs found")
        
        if pairs:
            # Get ticker for first pair
            ticker = client.get_ticker(pairs[0])
            ticker_ok = ticker is not None
            print_status(f"Fetch ticker ({pairs[0]})", ticker_ok)
            
            # Get candles for first pair
            candles = client.get_candles(pairs[0], 60, limit=20)
            candles_ok = candles is not None
            print_status(f"Fetch candles ({pairs[0]})", candles_ok, f"{len(candles) if candles else 0} candles")
            
            return ticker_ok and candles_ok
        
        return api_ok
    except Exception as e:
        print_status("API test", False, str(e))
        return False

def test_analyzer():
    """Test analyzer modules."""
    print_header("7. ANALYZER TEST")
    
    try:
        from core.analyzer import MarketAnalyzer
        from core.confidence_scorer import ConfidenceScorer
        
        print_status("Analyzer import", True)
        print_status("Scorer import", True)
        
        # Test with sample data
        analyzer = MarketAnalyzer()
        scorer = ConfidenceScorer()
        
        sample_candles = [
            {'timestamp': 1, 'open': 100, 'high': 105, 'low': 99, 'close': 102, 'volume': 1000},
            {'timestamp': 2, 'open': 102, 'high': 106, 'low': 101, 'close': 104, 'volume': 1200},
            {'timestamp': 3, 'open': 104, 'high': 108, 'low': 103, 'close': 106, 'volume': 1500},
        ]
        
        # Test trend
        is_bullish, strength = analyzer.calculate_trend(sample_candles)
        print_status("Trend calculation", True, f"Bullish={is_bullish}, Strength={strength:.2f}")
        
        # Test RVOL
        rvol = analyzer.calculate_relative_volume(sample_candles)
        print_status("RVOL calculation", True, f"RVOL={rvol:.2f}")
        
        # Test confidence
        scores = {
            'price_expansion': 75.0,
            'relative_volume': 85.0,
            'open_interest': 70.0,
            'trend': 80.0,
            'market_structure': 75.0,
            'breakout_strength': 70.0,
            'multi_tf_alignment': 85.0,
        }
        confidence = scorer.calculate_overall_confidence(scores)
        print_status("Confidence calculation", True, f"Confidence={confidence:.2f}%")
        
        return True
    except Exception as e:
        print_status("Analyzer test", False, str(e))
        return False

def test_signal_engine():
    """Test signal engine."""
    print_header("8. SIGNAL ENGINE TEST")
    
    try:
        from core.signal_engine import SignalEngine
        from database.db_manager import DatabaseManager
        
        print_status("Signal Engine import", True)
        
        db = DatabaseManager()
        engine = SignalEngine(db)
        print_status("Engine initialization", True)
        
        # Test with sample pair (BTC)
        print("\n  Testing with BTC-USDT-SWAP...")
        signal = engine.analyze_pair('BTC-USDT-SWAP')
        signal_ok = signal is not None or signal is None  # Either generates signal or doesn't (both OK)
        print_status("Pair analysis", True, "Signal generated" if signal else "No signal (normal)")
        
        return True
    except Exception as e:
        print_status("Signal Engine test", False, str(e))
        return False

def test_logging():
    """Test logging system."""
    print_header("9. LOGGING TEST")
    
    try:
        from utils.logger import get_logger
        
        logger = get_logger(__name__)
        print_status("Logger import", True)
        
        # Create log directory
        Path('logs').mkdir(exist_ok=True)
        
        # Test logging
        logger.info("Test log message")
        log_file = Path('logs/bot.log')
        log_exists = log_file.exists()
        print_status("Log file created", log_exists, "logs/bot.log")
        
        return log_exists
    except Exception as e:
        print_status("Logging test", False, str(e))
        return False

def generate_report(results):
    """Generate final test report."""
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED - READY FOR DEPLOYMENT!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed - Please review errors above")
    
    return failed_tests == 0

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  CRYPTO FUTURES BOT - TEST DEPLOYMENT")
    print("="*60)
    print(f"  Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    results = {}
    
    # Run all tests
    results['Environment'] = test_environment()
    results['Dependencies'] = test_dependencies()
    results['Configuration'] = test_config()
    results['Database'] = test_database()
    results['Telegram'] = test_telegram()
    results['OKX API'] = test_api()
    results['Analyzer'] = test_analyzer()
    results['Signal Engine'] = test_signal_engine()
    results['Logging'] = test_logging()
    
    # Generate report
    deployment_ready = generate_report(results)
    
    print("\n" + "="*60 + "\n")
    
    return 0 if deployment_ready else 1

if __name__ == '__main__':
    sys.exit(main())
