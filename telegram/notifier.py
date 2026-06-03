"""Telegram bot notifier for sending alerts."""
import requests
from datetime import datetime
from typing import Dict, List
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class TelegramNotifier:
    """Send notifications via Telegram."""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Chat ID to send messages to
        """
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or settings.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_signal_alert(self, signal: Dict) -> bool:
        """Send a trading signal alert.
        
        Args:
            signal: Signal dict
            
        Returns:
            True if successful
        """
        try:
            message = self._format_signal_message(signal)
            return self.send_message(message)
        except Exception as e:
            logger.error(f"Error sending signal alert: {str(e)}")
            return False
    
    def send_daily_summary(self, stats: Dict, top_coins: List[str]) -> bool:
        """Send daily market summary.
        
        Args:
            stats: Statistics dict
            top_coins: List of top opportunity coins
            
        Returns:
            True if successful
        """
        try:
            message = self._format_daily_summary(stats, top_coins)
            return self.send_message(message)
        except Exception as e:
            logger.error(f"Error sending daily summary: {str(e)}")
            return False
    
    def send_status_update(self, status: Dict) -> bool:
        """Send bot status update.
        
        Args:
            status: Status dict
            
        Returns:
            True if successful
        """
        try:
            message = self._format_status_message(status)
            return self.send_message(message)
        except Exception as e:
            logger.error(f"Error sending status update: {str(e)}")
            return False
    
    def send_message(self, message: str) -> bool:
        """Send a raw message to Telegram.
        
        Args:
            message: Message text
            
        Returns:
            True if successful
        """
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            logger.info("Message sent to Telegram")
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    @staticmethod
    def _format_signal_message(signal: Dict) -> str:
        """Format signal for Telegram message.
        
        Args:
            signal: Signal dict
            
        Returns:
            Formatted message
        """
        coin = signal.get('coin', 'UNKNOWN')
        action = signal.get('action', 'N/A')
        signal_type = signal.get('type', 'N/A')
        confidence = signal.get('confidence', 0)
        risk = signal.get('risk', 'N/A')
        reason = signal.get('reason', [])
        bot_view = signal.get('bot_view', '')
        price = signal.get('price', 0)
        timestamp = signal.get('timestamp', '')
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime('%Y-%m-%d %H:%M UTC')
        except:
            time_str = timestamp
        
        # Build message
        message = f"""🚨 <b>MARKET ALERT</b>

<b>Coin:</b> {coin}USDT
<b>Action:</b> <i>{action}</i>
<b>Type:</b> {signal_type}
<b>Confidence:</b> {confidence}%
<b>Risk:</b> {risk}

<b>Reason:</b>
"""
        
        if isinstance(reason, list):
            for r in reason:
                message += f"• {r}\n"
        else:
            message += f"• {reason}\n"
        
        message += f"""
<b>Bot View:</b>
{bot_view}

<b>Price:</b> {price}
<b>Time:</b> {time_str}
"""
        
        return message
    
    @staticmethod
    def _format_daily_summary(stats: Dict, top_coins: List[str]) -> str:
        """Format daily summary for Telegram.
        
        Args:
            stats: Statistics dict
            top_coins: Top coins list
            
        Returns:
            Formatted message
        """
        pairs_scanned = stats.get('pairs_scanned', 0)
        signals_generated = stats.get('signals_generated', 0)
        buy_signals = stats.get('buy_signals', 0)
        sell_signals = stats.get('sell_signals', 0)
        
        message = f"""📊 <b>DAILY MARKET REPORT</b>

<b>Pairs Scanned:</b> {pairs_scanned}
<b>Signals Generated:</b> {signals_generated}
<b>BUY LONG Signals:</b> {buy_signals}
<b>SELL SHORT Signals:</b> {sell_signals}

<b>Top Opportunities:</b>
"""
        
        for i, coin in enumerate(top_coins, 1):
            message += f"{i}. {coin}\n"
        
        return message
    
    @staticmethod
    def _format_status_message(status: Dict) -> str:
        """Format status message for Telegram.
        
        Args:
            status: Status dict
            
        Returns:
            Formatted message
        """
        pairs_scanned = status.get('pairs_scanned', 0)
        signals_today = status.get('signals_today', 0)
        last_scan = status.get('last_scan', 'Unknown')
        bot_status = status.get('status', 'OFFLINE')
        
        status_emoji = '✅' if bot_status == 'ONLINE' else '❌'
        
        message = f"""🤖 <b>Bot Status</b>

<b>Status:</b> {status_emoji} {bot_status}
<b>Pairs Scanned:</b> {pairs_scanned}
<b>Signals Today:</b> {signals_today}
<b>Last Scan:</b> {last_scan}
"""
        
        return message
