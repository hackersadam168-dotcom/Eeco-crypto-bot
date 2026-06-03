# EECO Crypto Futures Market Intelligence Bot

## Overview

A production-grade crypto futures market intelligence bot that continuously monitors the entire OKX USDT perpetual futures market, identifies high-probability trading opportunities, and sends actionable alerts to Telegram.

**This is NOT an auto-trading bot.** The bot performs analysis and sends alerts only. The user makes the final trading decision.

## Features

✅ **Hourly Market Scans** - 1-hour frequency scanning (no scalping)
✅ **Multi-Timeframe Analysis** - Intraday (15m, 1H) & Swing (4H, 1D)
✅ **Confidence Scoring** - 88+ confidence threshold for signals
✅ **Risk Classification** - LOW, MEDIUM, HIGH risk levels
✅ **Technical Analysis** - Price, Volume, OI, Trend, Market Structure
✅ **Duplicate Protection** - 6-hour cooldown per coin/signal
✅ **Telegram Alerts** - Real-time notifications with actionable insights
✅ **Signal History** - SQLite database with full signal logging
✅ **Daily Summaries** - Market report with top opportunities

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/officialstretchfitnesscenter-code/eeco-crypto-bot.git
cd eeco-crypto-bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from template:
```bash
cp .env.example .env
```

5. Configure credentials in `.env`:
```
# OKX API
OKX_API_KEY=your_key
OKX_API_SECRET=your_secret
OKX_API_PASSPHRASE=your_passphrase

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Bot Settings
SCAN_INTERVAL=3600
CONFIDENCE_THRESHOLD=88
COOLDOWN_HOURS=6
```

## Configuration

Edit `config/settings.py` to customize:

- **Timeframes**: Intraday (15m, 1H) & Swing (4H, 1D)
- **Confidence Weights**: Adjust scoring factors
- **Risk Thresholds**: Define risk levels
- **Min RVOL**: Relative volume minimum

## Running the Bot

```bash
python main.py
```

The bot will:
1. Scan all OKX USDT perpetual pairs
2. Analyze technical indicators
3. Generate high-confidence signals
4. Send alerts to Telegram
5. Store results in SQLite
6. Schedule next scan (1 hour later)

## Signal Analysis

The bot analyzes:

- **Price Expansion** - Price movement vs. historical average
- **Relative Volume (RVOL)** - Current vs. average volume
- **Open Interest (OI)** - OI changes and participation
- **Trend Direction** - Bullish/bearish trend confirmation
- **Market Structure** - Breakouts, breakdowns, ranges
- **Multi-Timeframe Alignment** - Multiple timeframe confirmation
- **Volatility** - Price stability assessment

## Confidence Scoring

Final confidence = Weighted average of all factors:

- Price Expansion: 15%
- Relative Volume: 20%
- Open Interest: 15%
- Trend: 15%
- Market Structure: 15%
- Breakout Strength: 10%
- Multi-TF Alignment: 10%

**Minimum Confidence Threshold: 88%**

## Signal Types

### Intraday (INTRADAY)
- Timeframes: 15m + 1H
- Duration: Hours to intraday
- Focus: Short-term momentum

### Swing (SWING)
- Timeframes: 4H + 1D
- Duration: Days to weeks
- Focus: Trend continuation

## Output Format

Example Telegram alert:

```
🚨 MARKET ALERT

Coin: XRPUSDT
Action: BUY LONG
Type: SWING
Confidence: 92%
Risk: LOW

Reason:
• RVOL 4.2x above average
• Open Interest +15%
• 4H resistance breakout
• Higher timeframe trend bullish

Bot View:
Current market structure favors upside continuation.

Price: 2.35
Time: 2026-06-02 18:00 UTC
```

## Database

Signals are stored in SQLite (`data/signals.db`):

- coin: Trading pair
- action: BUY LONG or SELL SHORT
- signal_type: INTRADAY or SWING
- confidence: 0-100 score
- risk: LOW, MEDIUM, HIGH
- reason: Analysis bullets
- bot_view: Market perspective
- price: Entry price
- timestamp: Alert time

## Telegram Commands (Coming Soon)

- `/top` - Top opportunities
- `/buy` - Latest BUY signals
- `/sell` - Latest SELL signals
- `/summary` - Daily market summary
- `/status` - Bot status

## Important Notes

⚠️ **This bot does NOT:**
- Execute trades
- Place orders
- Auto-buy or auto-sell
- Guarantee profits
- Connect to exchanges for trading

✅ **The user:**
- Receives alerts
- Performs final analysis
- Makes trading decisions
- Executes trades manually

## Error Handling

The bot includes:
- API error handling
- Connection retry logic
- Signal validation
- Logging to file and console

## Logs

Logs stored in `logs/bot.log`:
```
2026-06-03 12:00:01 - main - INFO - Starting market scan...
2026-06-03 12:00:15 - core.signal_engine - INFO - Signal generated for BTC-USDT-SWAP: BUY LONG
```

## Troubleshooting

### No signals generated
- Check confidence threshold (currently 88)
- Verify market volatility
- Review analysis logs

### API errors
- Verify OKX API credentials
- Check API key permissions
- Ensure internet connection

### Telegram not working
- Verify bot token and chat ID
- Check Telegram bot is active
- Review error logs

## Architecture

```
eeco-crypto-bot/
├── config/          # Configuration & settings
├── core/            # Analysis & signal generation
├── database/        # SQLite management
├── telegram/        # Telegram notifications
├── utils/           # Helper utilities
├── logs/            # Application logs
├── data/            # SQLite database
└── main.py          # Entry point
```

## Future Enhancements

- [ ] Telegram command handlers
- [ ] Web dashboard
- [ ] Advanced pattern recognition
- [ ] Risk management features
- [ ] Performance analytics
- [ ] Multi-exchange support

## Support

For issues, questions, or suggestions:
1. Check logs in `logs/bot.log`
2. Review configuration in `.env`
3. Verify API credentials

## Disclaimer

This bot is for market analysis and alerts only. Users are solely responsible for their trading decisions. Past performance does not guarantee future results. Always use proper risk management.

## License

MIT License

---

**Built with ❤️ for crypto traders**
