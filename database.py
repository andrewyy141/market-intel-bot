import aiosqlite
import os
from datetime import datetime
from config.settings import DB_PATH

async def init_database():
    """Initialize SQLite database with schema"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Signals table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                category TEXT NOT NULL,
                headline TEXT NOT NULL,
                details TEXT,
                confidence REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                source_url TEXT,
                is_opinion BOOLEAN DEFAULT 0,
                alerted BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Content cache (for deduplication)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS content_cache (
                content_hash TEXT PRIMARY KEY,
                ticker TEXT,
                source TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Alert history (track what we sent to Discord)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER,
                ticker TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY (signal_id) REFERENCES signals(id)
            )
        ''')
        
        # Cooldown tracking
        await db.execute('''
            CREATE TABLE IF NOT EXISTS ticker_cooldowns (
                ticker TEXT PRIMARY KEY,
                last_alert DATETIME NOT NULL
            )
        ''')
        
        await db.commit()
        print("✅ Database initialized")

async def save_signal(signal_data):
    """Save detected signal to database"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO signals 
            (ticker, signal_type, category, headline, details, confidence, timestamp, source_url, is_opinion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            signal_data['ticker'],
            signal_data['signal_type'],
            signal_data['category'],
            signal_data['headline'],
            signal_data['details'],
            signal_data['confidence'],
            signal_data['timestamp'],
            signal_data['source_url'],
            signal_data.get('is_opinion', False)
        ))
        await db.commit()
        return db.lastrowid

async def is_duplicate(content_hash):
    """Check if content has been seen before"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            'SELECT 1 FROM content_cache WHERE content_hash = ?',
            (content_hash,)
        ) as cursor:
            result = await cursor.fetchone()
            return result is not None

async def cache_content(content_hash, ticker, source):
    """Cache content hash to prevent duplicates"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR IGNORE INTO content_cache (content_hash, ticker, source)
            VALUES (?, ?, ?)
        ''', (content_hash, ticker, source))
        await db.commit()

async def is_on_cooldown(ticker, hours=4):
    """Check if ticker is on cooldown (prevent spam)"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT last_alert FROM ticker_cooldowns
            WHERE ticker = ?
            AND datetime(last_alert, '+' || ? || ' hours') > datetime('now')
        ''', (ticker, hours)) as cursor:
            result = await cursor.fetchone()
            return result is not None

async def update_cooldown(ticker):
    """Update cooldown timestamp for ticker"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO ticker_cooldowns (ticker, last_alert)
            VALUES (?, datetime('now'))
        ''', (ticker,))
        await db.commit()

async def get_alerts_today():
    """Get number of alerts sent today"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT COUNT(*) FROM alert_history
            WHERE date(timestamp) = date('now')
        ''') as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def log_alert(signal_id, ticker):
    """Log that we sent an alert"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO alert_history (signal_id, ticker, timestamp)
            VALUES (?, ?, datetime('now'))
        ''', (signal_id, ticker))
        await db.commit()