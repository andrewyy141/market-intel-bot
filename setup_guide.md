Market Intelligence Discord Bot - Setup Guide
Complete setup guide to get your bot running in under 30 minutes.

📋 Prerequisites
Python 3.11 or higher
Discord account
GitHub account (for deployment)
15-30 minutes
🚀 Step-by-Step Setup
Step 1: Create Discord Bot
Go to Discord Developer Portal
Click "New Application" → Name it "Market Intel Bot"
Go to "Bot" tab → Click "Add Bot"
Under Token, click "Reset Token" and copy it (save this!)
Enable these Privileged Gateway Intents:
✅ Message Content Intent
✅ Server Members Intent (optional)
Go to "OAuth2" → "URL Generator"
Select scopes:
✅ bot
✅ applications.commands
Select bot permissions:
✅ Send Messages
✅ Embed Links
✅ Read Message History
Copy the generated URL and open it in browser
Select your Discord server and authorize
Step 2: Get Channel ID
Open Discord, go to User Settings → Advanced
Enable Developer Mode
Right-click the channel where you want alerts → Copy Channel ID
Step 3: Get FRED API Key (Free)
Go to FRED API Key Request
Click "Request API Key"
Fill out simple form (takes 30 seconds)
Copy your API key from email
Step 4: Download & Setup Project
Option A: Local Setup (Recommended for Testing)
bash
# Clone/create project directory
mkdir market-intel-bot
cd market-intel-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Save all the provided code files into the directory structure:
# bot.py
# requirements.txt
# config/settings.py
# config/sources.py
# database/models.py
# ingestion/sec_edgar.py
# ingestion/rss_feeds.py
# ingestion/fred_data.py
# ingestion/yahoo_finance.py
# processing/validator.py
# processing/extractor.py
# processing/sentiment.py
# signals/detector.py
# signals/rules.py
# discord_bot/formatter.py

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (for NLP)
python -m spacy download en_core_web_sm
Option B: Deploy to Render.com (Free Hosting)
Create GitHub repository
Push all code to GitHub
Go to Render.com
Click "New +" → "Background Worker"
Connect your GitHub repo
Configure:
Name: market-intel-bot
Runtime: Python 3
Build Command: pip install -r requirements.txt && python -m spacy download en_core_web_sm
Start Command: python bot.py
Add environment variables (see Step 5)
Step 5: Configure Environment Variables
Create .env file in project root:

bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env  # or use any text editor
Fill in:

DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_FROM_STEP_1
ALERT_CHANNEL_ID=YOUR_CHANNEL_ID_FROM_STEP_2
FRED_API_KEY=YOUR_FRED_KEY_FROM_STEP_3
Step 6: Create Required Directories
bash
mkdir -p data logs
touch data/.gitkeep logs/.gitkeep
Step 7: Run the Bot
Local Run:
bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run bot
python bot.py
You should see:

✅ MarketIntelBot#1234 is now running!
📡 Monitoring 1 channel(s)
✅ Database initialized
✅ FinBERT sentiment analyzer loaded
🔄 Signal detection loop started
⏳ Waiting 30 seconds before first scan...
Deploy to Render:
Just push to GitHub, Render auto-deploys
Check logs in Render dashboard
📁 Project Structure
market-intel-bot/
├── bot.py                      # Main entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (SECRET!)
├── .env.example               # Template for .env
├── README.md                  # Project documentation
├── SETUP_GUIDE.md            # This file
│
├── config/
│   ├── __init__.py
│   ├── settings.py           # Bot configuration
│   └── sources.py            # Data source URLs
│
├── database/
│   ├── __init__.py
│   └── models.py             # Database schema & queries
│
├── ingestion/
│   ├── __init__.py
│   ├── sec_edgar.py          # SEC filings
│   ├── rss_feeds.py          # News RSS feeds
│   ├── fred_data.py          # Economic data
│   └── yahoo_finance.py      # Earnings data
│
├── processing/
│   ├── __init__.py
│   ├── validator.py          # Content filtering
│   ├── extractor.py          # Entity extraction
│   └── sentiment.py          # Sentiment analysis
│
├── signals/
│   ├── __init__.py
│   ├── detector.py           # Main signal detection
│   └── rules.py              # Rules engine
│
├── discord_bot/
│   ├── __init__.py
│   └── formatter.py          # Discord embed formatting
│
├── data/
│   └── market_intel.db       # SQLite database (auto-created)
│
└── logs/
    └── bot.log               # Application logs (optional)
🧪 Testing the Bot
Once running, test with Discord commands:

!ping          # Check if bot is alive
!status        # View bot statistics
!watchlist     # See monitored tickers
The bot will automatically:

Scan for signals every 15 minutes
Post alerts to your designated channel
Respect cooldown periods (4 hours per ticker)
Limit to 10 alerts per day
🔧 Customization
Change Watchlist
Edit config/settings.py:

python
# Add your custom tickers
CUSTOM_TICKERS = ['SHOP', 'SQ', 'COIN']
WATCHLIST = list(set(MAG7 + AI_STOCKS + CUSTOM_TICKERS))
Adjust Thresholds
Edit config/settings.py:

python
MIN_CONFIDENCE = 0.75        # Lower = more alerts (default: 0.80)
MAX_ALERTS_PER_DAY = 15      # Increase daily limit (default: 10)
COOLDOWN_HOURS = 2           # Reduce cooldown (default: 4)
Add Custom Rules
Edit signals/rules.py and add your rule:

python
# Rule: Large price moves
if content.get('source') == 'Yahoo Finance':
    price_change = content.get('change_pct', 0)
    if abs(price_change) > 5:  # 5%+ move
        return {
            'signal_type': 'price_move',
            'category': 'Micro → Price Action',
            'confidence': 0.80,
            'context': f'Large price move: {price_change:+.1f}%'
        }
📊 Expected Alert Examples
Example 1: Earnings Beat
🔴 NVDA - Earnings

📊 Category: Micro → Earnings
🟢 Confidence: 90%
📈 Sentiment: BULLISH

💡 Details:
EPS: $5.16 vs $4.64 est (+11.2%)
Revenue: $35.1B vs $33.2B est

🔗 Source: [Yahoo Finance](...)
Example 2: SEC Filing
🔴 AAPL - Sec Filing

📊 Category: Micro → Material Event
🟢 Confidence: 95%
➡️ Sentiment: NEUTRAL

💡 Details:
8-K filing indicates material corporate event
Item 8.01 - Other Event

🔗 Source: [SEC Edgar](...)
Example 3: Macro Data
📊 CPI - Macro Data

📊 Category: Macro → CPI
🟡 Confidence: 85%
📉 Sentiment: BEARISH

💡 Details:
CPI changed +0.4%
Above expected +0.2%

🔗 Source: [FRED](...)
🐛 Troubleshooting
Bot doesn't start
Issue: DISCORD_BOT_TOKEN not found

Fix: Make sure .env file exists and has valid token
Issue: Channel not found

Fix: Enable Developer Mode in Discord, copy correct Channel ID
No alerts appearing
Issue: Bot is running but no alerts

Fix: Wait 15 minutes for first scan cycle
Check: Run !status to verify bot is active
Debug: Check if watchlist has active tickers
Import errors
Issue: ModuleNotFoundError

Fix: Run pip install -r requirements.txt again
Fix: Make sure virtual environment is activated
FinBERT not loading
Issue: Sentiment analysis disabled

Fix: This is OK - bot still works without it
Fix: If you want it, ensure enough RAM (2GB+)
💰 Cost Breakdown (All Free!)
Service	Free Tier	Usage
Discord Bot	✅ Unlimited	Hosting bot
FRED API	✅ 120 req/day	Economic data
SEC EDGAR	✅ Unlimited	Company filings
Yahoo Finance	✅ Unlimited	Earnings/prices
RSS Feeds	✅ Unlimited	News ingestion
Render.com	✅ 750 hrs/mo	Bot hosting
Total Monthly Cost: $0

📈 Next Steps
Once running successfully:

Monitor for 48 hours - Verify alerts are high-quality
Adjust thresholds - Tune confidence levels if too many/few alerts
Add custom rules - Tailor to your trading style
Expand watchlist - Add sectors you trade
Set up logging - Track bot performance over time
🆘 Support
If you encounter issues:

Check logs: tail -f logs/bot.log
Verify all dependencies installed
Ensure API keys are valid
Test with !ping command
Check Discord bot has proper permissions
🔒 Security Notes
⚠️ NEVER commit .env to GitHub!

Add to .gitignore:

.env
data/
logs/
__pycache__/
*.pyc
venv/
✅ Quick Start Checklist
 Discord bot created
 Bot invited to server
 Channel ID copied
 FRED API key obtained
 .env file configured
 Dependencies installed
 Bot running locally
 Test commands working (!ping)
 First scan completed
 Alerts appearing in channel
You're done! 🎉

Your Market Intelligence Bot is now monitoring the market 24/7 and will alert you to high-confidence trading signals.

