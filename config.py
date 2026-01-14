import os
from dotenv import load_dotenv

load_dotenv()

# Discord
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
ALERT_CHANNEL_ID = int(os.getenv('ALERT_CHANNEL_ID', 0))

# API Keys
FRED_API_KEY = os.getenv('FRED_API_KEY', '')

# Stock Universe
MAG7 = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']

AI_STOCKS = [
    'NVDA', 'AMD', 'AVGO', 'MRVL', 'PLTR', 'SNOW',
    'TSM', 'ASML', 'ARM', 'SMCI', 'ANET', 'DDOG'
]

HIGH_QUALITY_GROWTH = ['COST', 'V', 'MA', 'UNH', 'LLY', 'JNJ']
VALUE_PLAYS = ['INTC', 'BAC', 'WFC', 'XOM', 'CVX']

WATCHLIST = list(set(MAG7 + AI_STOCKS + HIGH_QUALITY_GROWTH + VALUE_PLAYS))

# Signal Thresholds
MIN_CONFIDENCE = 0.80
MAX_ALERTS_PER_DAY = 10
COOLDOWN_HOURS = 4

# Trusted Sources
TRUSTED_SOURCES = [
    'SEC',
    'FRED',
    'Reuters',
    'Federal Reserve',
    'Company IR',
    'Yahoo Finance'
]

# Sponsored Content Keywords (for filtering)
SPONSORED_KEYWORDS = [
    'sponsored', 'paid promotion', 'partnered content',
    'advertisement', 'advertorial', 'brand studio',
    'native advertising', 'presented by'
]

# Opinion URL Patterns (for filtering)
OPINION_URL_PATTERNS = [
    '/opinion/', '/commentary/', '/analysis/',
    '/blog/', '?utm_source=', '?ref=affiliate'
]

# Database
DB_PATH = 'data/market_intel.db'

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/bot.log'