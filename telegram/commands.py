#!/usr/bin/env python3
"""Telegram bot commands handler."""
import logging
from typing import Optional, Dict
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database.db_manager import DatabaseManager
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class TelegramCommandHandler:
    """Handle Telegram bot commands."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize command handler.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager or DatabaseManager()
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = int(settings.TELEGRAM_CHAT_ID)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start command handler."""
        welcome_message = """🤖 <b>CRYPTO FUTURES MARKET INTELLIGENCE BOT</b>

This bot scans OKX USDT perpetual futures and sends high-confidence trading alerts.

<b>Available Commands:</b>
/status - Bot status & today's summary
/top - Top 5 opportunities today
/buy - BUY LONG signals today
/sell - SELL SHORT signals today
/summary - Daily market report
/help - Show help message

<b>Alert Details Include:</b>
✅ Confidence Score (Min 88%)
✅ Risk Level (LOW/MEDIUM/HIGH)
✅ Reasoning (RVOL, OI, Structure, etc)
✅ Current Price
✅ Timeframe Classification

<b>Trading Styles:</b>
📈 INTRADAY (15m + 1H)
📊 SWING (4H + 1D)

<b>Important:</b>
⚠️ User always makes final trading decision
⚠️ Bot never executes trades
⚠️ For market intelligence only
"""
        await update.message.reply_text(welcome_message, parse_mode='HTML')
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Bot status command."""
        try:
            total, buy_long, sell_short = self.db.get_signal_count_today()
            
            status_message = f"""🤖 <b>BOT STATUS</b>

<b>Status:</b> ✅ ONLINE

<b>Today's Signals:</b>
• Total: {total}
• BUY LONG: {buy_long}
• SELL SHORT: {sell_short}

<b>Configuration:</b>
• Scan Interval: {settings.SCAN_INTERVAL}s (1 hour)
• Confidence Threshold: {settings.CONFIDENCE_THRESHOLD}%
• Cooldown: {settings.COOLDOWN_HOURS}h per coin
• Pairs Scanned: 100+ USDT perpetuals

<b>Trading Styles:</b>
📈 Intraday (15m, 1H)
📊 Swing (4H, 1D)

<b>Next Scan:</b> In ~60 minutes
"""
            await update.message.reply_text(status_message, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Error in status command: {str(e)}")
            await update.message.reply_text("❌ Error fetching status")
    
    async def top(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Top opportunities command."""
        try:
            signals = self.db.get_top_opportunities(limit=5)
            
            if not signals:
                await update.message.reply_text("📊 No signals generated yet today")
                return
            
            message = "🏆 <b>TOP 5 OPPORTUNITIES TODAY</b>\n\n"
            for i, signal in enumerate(signals, 1):
                coin = signal[1]
                action = signal[2]
                confidence = signal[4]
                risk = signal[5]
                
                emoji = "🟢" if action == "BUY LONG" else "🔴"
                message += f"{i}. {emoji} <b>{coin}</b>\n"
                message += f"   Action: {action}\n"
                message += f"   Confidence: {confidence}%\n"
                message += f"   Risk: {risk}\n\n"
            
            await update.message.reply_text(message, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Error in top command: {str(e)}")
            await update.message.reply_text("❌ Error fetching top opportunities")
    
    async def buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """BUY LONG signals command."""
        try:
            signals = self.db.get_signals_today()
            buy_signals = [s for s in signals if s[2] == 'BUY LONG']
            
            if not buy_signals:
                await update.message.reply_text("📊 No BUY LONG signals today")
                return
            
            message = f"🟢 <b>BUY LONG SIGNALS TODAY ({len(buy_signals)})</b>\n\n"
            for signal in buy_signals[:10]:  # Show top 10
                coin = signal[1]
                confidence = signal[4]
                signal_type = signal[3]
                
                message += f"<b>{coin}</b>\n"
                message += f"Type: {signal_type} | Confidence: {confidence}%\n\n"
            
            await update.message.reply_text(message, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Error in buy command: {str(e)}")
            await update.message.reply_text("❌ Error fetching BUY signals")
    
    async def sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """SELL SHORT signals command."""
        try:
            signals = self.db.get_signals_today()
            sell_signals = [s for s in signals if s[2] == 'SELL SHORT']
            
            if not sell_signals:
                await update.message.reply_text("📊 No SELL SHORT signals today")
                return
            
            message = f"🔴 <b>SELL SHORT SIGNALS TODAY ({len(sell_signals)})</b>\n\n"
            for signal in sell_signals[:10]:  # Show top 10
                coin = signal[1]
                confidence = signal[4]
                signal_type = signal[3]
                
                message += f"<b>{coin}</b>\n"
                message += f"Type: {signal_type} | Confidence: {confidence}%\n\n"
            
            await update.message.reply_text(message, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Error in sell command: {str(e)}")
            await update.message.reply_text("❌ Error fetching SELL signals")
    
    async def summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Daily summary command."""
        try:
            total, buy_long, sell_short = self.db.get_signal_count_today()
            top_opportunities = self.db.get_top_opportunities(limit=3)
            
            message = """📊 <b>DAILY MARKET REPORT</b>

<b>Signals Generated:</b>
• Total: """ + str(total) + """
• BUY LONG: """ + str(buy_long) + """
• SELL SHORT: """ + str(sell_short) + """

<b>Top Opportunities:</b>
"""
            for i, signal in enumerate(top_opportunities, 1):
                coin = signal[1]
                confidence = signal[4]
                message += f"{i}. {coin} ({confidence}%)\n"
            
            message += f"""
<b>Market Analysis:</b>
• Pairs Scanned: 100+ USDT perpetuals
• Timeframes: 15m, 1H, 4H, 1D
• Confidence Threshold: 88%
• Cooldown: 6 hours per coin

⚠️ All alerts for intelligence only
⚠️ User decides final trading action
"""
            await update.message.reply_text(message, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Error in summary command: {str(e)}")
            await update.message.reply_text("❌ Error fetching summary")
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Help command."""
        help_message = """📖 <b>BOT COMMANDS</b>

<b>Information:</b>
/start - Welcome message
/help - This message
/status - Bot status

<b>Signal Queries:</b>
/top - Top 5 opportunities
/buy - BUY LONG signals today
/sell - SELL SHORT signals today
/summary - Daily report

<b>Signal Format:</b>
🚨 MARKET ALERT
├─ Coin: XRPUSDT
├─ Action: BUY LONG / SELL SHORT
├─ Type: INTRADAY / SWING
├─ Confidence: 88%+ (minimum)
├─ Risk: LOW / MEDIUM / HIGH
├─ Reason: (RVOL, OI, Structure, etc)
└─ Price: Current market price

<b>Important Restrictions:</b>
✅ Scan Interval: 1 hour (no scalping)
✅ No auto-trading (user decides)
✅ No HOLD alerts (only BUY/SELL)
✅ High confidence only (88%+)
✅ Quality over quantity

<b>Data Analyzed:</b>
📊 Price, Volume, RVOL, OI
📈 Trend, Structure, Breakouts
🔗 Multi-timeframe alignment
⚡ Market volatility

Need help? Contact bot administrator.
"""
        await update.message.reply_text(help_message, parse_mode='HTML')

def setup_telegram_commands(db_manager: DatabaseManager = None) -> Optional[Application]:
    """Setup Telegram command handlers.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        Telegram Application or None
    """
    try:
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.warning("⚠️ Telegram bot token not configured")
            return None
        
        app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        handler = TelegramCommandHandler(db_manager)
        
        # Add command handlers
        app.add_handler(CommandHandler("start", handler.start))
        app.add_handler(CommandHandler("status", handler.status))
        app.add_handler(CommandHandler("top", handler.top))
        app.add_handler(CommandHandler("buy", handler.buy))
        app.add_handler(CommandHandler("sell", handler.sell))
        app.add_handler(CommandHandler("summary", handler.summary))
        app.add_handler(CommandHandler("help", handler.help))
        
        logger.info("Telegram commands configured successfully")
        return app
    except Exception as e:
        logger.error(f"Error setting up Telegram commands: {str(e)}")
        return None
