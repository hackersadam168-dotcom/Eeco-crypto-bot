# CRYPTO FUTURES BOT - NO API KEYS NEEDED 🎉

## ✅ WORKS IN INDIA - NO REGISTRATION REQUIRED

Bot now uses **PUBLIC DATA ONLY** - No API keys needed:
- ✅ Works in India (100% legal)
- ✅ No registration required
- ✅ No API credentials needed
- ✅ Free & open source
- ✅ Public market data
- ✅ CoinGecko + Coinglass free APIs

---

## ⚡ INSTANT START (1 MINUTE)

### Step 1: Clone Repository
```bash
git clone https://github.com/officialstretchfitnesscenter-code/Eeco-crypto-bot.git
cd Eeco-crypto-bot
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Start Bot
```bash
python main.py
```

Alerts appear on Telegram! 🚀

---

## 📊 PUBLIC DATA SOURCES (FREE)

### 1. CoinGecko API
- ✅ Free tier (no key needed)
- ✅ 10+ calls/second
- ✅ OHLCV data
- ✅ 1000+ cryptocurrencies
- ✅ Volume data
- ✅ Market cap

### 2. Coinglass API
- ✅ Free public data
- ✅ Open interest data
- ✅ Funding rates
- ✅ Liquidation data
- ✅ Long/Short ratio

### 3. CoinMarketCap Free API
- ✅ Basic free tier
- ✅ Price data
- ✅ Volume data
- ✅ Market data

---

## 🎯 WHAT BOT SCANS (NO CREDENTIALS)

**Every Hour:**
1. ✅ Fetches 100+ crypto pairs from CoinGecko
2. ✅ Gets 1H, 4H, 1D candle data
3. ✅ Analyzes price trends
4. ✅ Calculates volume metrics
5. ✅ Gets open interest from Coinglass
6. ✅ Generates signals (88+ confidence)
7. ✅ Sends Telegram alerts
8. ✅ Stores in SQLite database

---

## 🚀 QUICK START

### Windows/Mac/Linux

```bash
# 1. Install Python 3.8+
# https://www.python.org/downloads/

# 2. Clone & setup
git clone https://github.com/officialstretchfitnesscenter-code/Eeco-crypto-bot.git
cd Eeco-crypto-bot

# 3. Install packages
pip install -r requirements.txt

# 4. Edit .env (only Telegram needed - already configured)
nano .env
# TELEGRAM_BOT_TOKEN=8854251990:AAFOxZfQGP6dKYTExEL7YByAvf69Djnflqo ✓
# TELEGRAM_CHAT_ID=1490359174 ✓
# (That's it! No API keys needed)

# 5. Test
python verify_local.py

# 6. Start
python main.py
```

### Android Phone (Termux)

```bash
# 1. Install Termux from Play Store

# 2. In Termux:
pkg update && pkg upgrade -y
pkg install python git

# 3. Clone
git clone https://github.com/officialstretchfitnesscenter-code/Eeco-crypto-bot.git
cd Eeco-crypto-bot

# 4. Install
pip install -r requirements.txt

# 5. Run
nohup python main.py > bot.log 2>&1 &

# Check logs:
tail -f bot.log
```

---

## 📝 .ENV FILE (MINIMAL)

```bash
# Only 2 lines needed (already configured):
TELEGRAM_BOT_TOKEN=8854251990:AAFOxZfQGP6dKYTExEL7YByAvf69Djnflqo
TELEGRAM_CHAT_ID=1490359174

# Optional customization:
SCAN_INTERVAL=3600          # 1 hour (in seconds)
CONFIDENCE_THRESHOLD=88     # Minimum confidence for alerts
COOLDOWN_HOURS=6            # Wait between same coin signals
LOG_LEVEL=INFO              # INFO or DEBUG
```

---

## 📊 EXAMPLE TELEGRAM ALERT

```
🚨 MARKET ALERT

Coin: XRPUSDT
Action: BUY LONG
Type: SWING
Confidence: 92%
Risk: LOW

Reason:
• Volume surge detected
• Bullish trend confirmed
• Support held strong
• Open interest increasing

Bot View:
Market structure favors upside continuation.

Price: $2.35
Time: 2026-06-03 18:00 UTC
```

---

## 🧪 TESTING

### Verify Setup
```bash
python verify_local.py
```

Should show all ✅ checks.

### Full Test (Exchange → Telegram)
```bash
python test_e2e.py
```

Tests complete flow.

### Check Bot Status
```bash
# View logs
tail -f logs/bot.log

# Check if running
ps aux | grep main.py

# View signals generated
sqlite3 data/signals.db "SELECT coin, action, confidence FROM signals ORDER BY timestamp DESC LIMIT 10;"
```

---

## 🎯 DATA FLOW (NO CREDENTIALS)

```
CoinGecko API (Free)
        ↓
Coinglass API (Free)
        ↓
Technical Analysis
        ↓
Confidence Scoring
        ↓
Signal Generation
        ↓
SQLite Database
        ↓
Telegram Alert
```

**All public APIs - No login needed!**

---

## ⚙️ CUSTOMIZE

### Get More Signals
```bash
echo "CONFIDENCE_THRESHOLD=75" >> .env
echo "COOLDOWN_HOURS=3" >> .env
python main.py
```

### Get Better Quality
```bash
echo "CONFIDENCE_THRESHOLD=92" >> .env
echo "COOLDOWN_HOURS=12" >> .env
python main.py
```

### Scan Different Pairs

Edit `core/coingecko_api.py`, line ~120:
```python
# Change from 100 to 50 pairs:
return sorted(usdt_pairs)[:50]
```

---

## 📱 KEEP RUNNING 24/7

### On Computer

**Windows:**
```bash
start /b python main.py
```

**Mac/Linux:**
```bash
nohup python main.py > bot.log 2>&1 &
```

**Better (Using Screen):**
```bash
screen -S bot
python main.py
# Ctrl+A then D to detach

screen -r bot  # Reattach
```

### On Android (Termux)

```bash
nohup python main.py > bot.log 2>&1 &

# Check if running:
ps aux | grep python

# View logs:
tail -f bot.log
```

**Bot keeps running even after closing Termux!**

---

## 🔧 TROUBLESHOOTING

### "No signals generated"

NORMAL! Bot only sends when:
- ✅ Confidence ≥ 88%
- ✅ Market conditions align
- ✅ Not on cooldown

To test with lower threshold:
```bash
echo "CONFIDENCE_THRESHOLD=70" >> .env
python main.py
```

### "Connection timeout"

```bash
# Test API connections
python -c "from core.coingecko_api import CoinGeckoClient; print(CoinGeckoClient().test_connection())"
```

### "Telegram not sending"

```bash
# Test Telegram
python -c "from telegram.notifier import TelegramNotifier; TelegramNotifier().send_message('Test')"
```

### "Module not found"

```bash
# Install all packages
pip install -r requirements.txt --upgrade
```

---

## ✅ CHECKLIST

- [ ] Python 3.8+ installed
- [ ] Repository cloned
- [ ] `pip install -r requirements.txt` done
- [ ] Telegram credentials in .env ✓ (already done)
- [ ] `python verify_local.py` passed ✅
- [ ] Bot started: `python main.py`
- [ ] Telegram alerts received 🎉

---

## 🎉 NO API KEYS NEEDED

✅ **100% Free**  
✅ **Works in India**  
✅ **No registration**  
✅ **No restrictions**  
✅ **Open source**  
✅ **Public data only**  
✅ **Telegram alerts**  

---

## 🚀 GET STARTED NOW

```bash
git clone https://github.com/officialstretchfitnesscenter-code/Eeco-crypto-bot.git
cd Eeco-crypto-bot
pip install -r requirements.txt
python main.py
```

**That's it! Alerts on Telegram! 📱**

---

## 📞 QUICK REFERENCE

| Command | Purpose |
|---------|----------|
| `python main.py` | Start bot |
| `python verify_local.py` | Test setup |
| `python test_e2e.py` | Full test |
| `tail -f logs/bot.log` | View logs |
| `ps aux \| grep main.py` | Check if running |
| `sqlite3 data/signals.db` | View database |
| `Ctrl+C` | Stop bot |

---

## 🎯 WORKS IN INDIA ✅

✅ **CoinGecko** - Works everywhere  
✅ **Coinglass** - Works everywhere  
✅ **No VPN needed**  
✅ **No registration**  
✅ **100% legal**  
✅ **Free forever**  

---

**Happy trading! 🚀**
