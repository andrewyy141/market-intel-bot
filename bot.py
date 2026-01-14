import discord
from discord.ext import commands, tasks
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import DISCORD_BOT_TOKEN, ALERT_CHANNEL_ID, MAX_ALERTS_PER_DAY, COOLDOWN_HOURS
from database.models import (
    init_database, save_signal, is_on_cooldown, 
    update_cooldown, get_alerts_today, log_alert
)
from ingestion.sec_edgar import SECIngestor
from ingestion.rss_feeds import RSSIngestor
from ingestion.fred_data import FREDIngestor
from ingestion.yahoo_finance import YahooFinanceIngestor
from processing.validator import ContentValidator
from signals.detector import SignalDetector
from discord_bot.formatter import AlertFormatter

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize components
sec_ingestor = SECIngestor()
rss_ingestor = RSSIngestor()
fred_ingestor = FREDIngestor()
yahoo_ingestor = YahooFinanceIngestor()
validator = ContentValidator()
detector = SignalDetector()
formatter = AlertFormatter()

@bot.event
async def on_ready():
    """Bot startup"""
    print(f'✅ {bot.user} is now running!')
    print(f'📡 Monitoring {len(ALERT_CHANNEL_ID)} channel(s)')
    
    # Initialize database
    await init_database()
    
    # Start background tasks
    check_signals.start()
    print('🔄 Signal detection loop started')

@bot.command()
async def ping(ctx):
    """Test if bot is responsive"""
    await ctx.send('🏓 Pong! Bot is alive and monitoring.')

@bot.command()
async def status(ctx):
    """Show bot status and statistics"""
    alerts_today = await get_alerts_today()
    
    embed = discord.Embed(
        title="📊 Bot Status",
        color=discord.Color.green()
    )
    embed.add_field(name="Alerts Today", value=f"{alerts_today}/{MAX_ALERTS_PER_DAY}", inline=True)
    embed.add_field(name="Status", value="🟢 Active", inline=True)
    embed.add_field(
        name="Monitoring",
        value=f"SEC Filings, News Feeds, Economic Data, Earnings",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def watchlist(ctx):
    """Show current watchlist"""
    from config.settings import WATCHLIST
    
    # Group by category
    from config.settings import MAG7, AI_STOCKS, HIGH_QUALITY_GROWTH, VALUE_PLAYS
    
    embed = discord.Embed(
        title="📈 Watchlist",
        description=f"Monitoring {len(WATCHLIST)} tickers",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Mag 7", value=', '.join(MAG7), inline=False)
    embed.add_field(name="AI Stocks", value=', '.join(AI_STOCKS[:10]), inline=False)
    embed.add_field(name="High Quality Growth", value=', '.join(HIGH_QUALITY_GROWTH), inline=False)
    embed.add_field(name="Value Plays", value=', '.join(VALUE_PLAYS), inline=False)
    
    await ctx.send(embed=embed)

@tasks.loop(minutes=15)
async def check_signals():
    """Main signal detection loop - runs every 15 minutes"""
    print(f"\n🔍 Checking for signals... {discord.utils.utcnow().strftime('%H:%M:%S')}")
    
    channel = bot.get_channel(ALERT_CHANNEL_ID)
    if channel is None:
        print("❌ Alert channel not found!")
        return
    
    try:
        # Check if we've hit daily limit
        alerts_today = await get_alerts_today()
        if alerts_today >= MAX_ALERTS_PER_DAY:
            print(f"⚠️  Daily alert limit reached ({alerts_today}/{MAX_ALERTS_PER_DAY})")
            return
        
        # Collect data from all sources
        all_content = []
        
        print("  📄 Fetching SEC filings...")
        sec_content = await sec_ingestor.get_recent_filings(hours=24)
        all_content.extend(sec_content)
        print(f"     Found {len(sec_content)} filings")
        
        print("  📰 Fetching news feeds...")
        news_content = await rss_ingestor.get_recent_news(hours=24)
        all_content.extend(news_content)
        print(f"     Found {len(news_content)} news items")
        
        print("  📊 Fetching economic data...")
        fred_content = await fred_ingestor.get_recent_data(hours=24)
        all_content.extend(fred_content)
        print(f"     Found {len(fred_content)} data points")
        
        print("  💰 Fetching earnings data...")
        earnings_content = await yahoo_ingestor.get_earnings_data()
        all_content.extend(earnings_content)
        print(f"     Found {len(earnings_content)} earnings events")
        
        print(f"\n  📥 Total content items: {len(all_content)}")
        
        # Process each item
        signals_detected = []
        for content in all_content:
            # Validate content
            is_valid, reason = await validator.is_valid(content)
            if not is_valid:
                continue
            
            # Detect signal
            signal = await detector.detect(content)
            if signal:
                signals_detected.append(signal)
        
        print(f"  ✅ Signals detected: {len(signals_detected)}")
        
        # Sort by confidence and send top signals
        signals_detected.sort(key=lambda x: x['confidence'], reverse=True)
        
        alerts_sent = 0
        for signal in signals_detected:
            # Check cooldown
            if await is_on_cooldown(signal['ticker'], hours=COOLDOWN_HOURS):
                print(f"  ⏳ Skipping {signal['ticker']} (cooldown)")
                continue
            
            # Check daily limit
            if alerts_today + alerts_sent >= MAX_ALERTS_PER_DAY:
                print(f"  ⚠️  Daily limit reached, stopping")
                break
            
            # Save signal to database
            signal_id = await save_signal(signal)
            
            # Send alert
            embed = formatter.format_signal(signal)
            await channel.send(embed=embed)
            
            # Update tracking
            await update_cooldown(signal['ticker'])
            await log_alert(signal_id, signal['ticker'])
            
            alerts_sent += 1
            print(f"  📢 Alert sent: {signal['ticker']} - {signal['signal_type']}")
            
            # Rate limit (1 alert per 5 seconds)
            await asyncio.sleep(5)
        
        print(f"\n✅ Scan complete. Sent {alerts_sent} alerts.\n")
        
    except Exception as e:
        print(f"❌ Error in signal detection loop: {e}")
        import traceback
        traceback.print_exc()

@check_signals.before_loop
async def before_check_signals():
    """Wait for bot to be ready before starting loop"""
    await bot.wait_until_ready()
    print("⏳ Waiting 30 seconds before first scan...")
    await asyncio.sleep(30)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `!help` to see available commands.")
    else:
        await ctx.send(f"❌ Error: {str(error)}")
        print(f"Command error: {error}")

# Run bot
if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN not found in .env file!")
        sys.exit(1)
    
    if not ALERT_CHANNEL_ID:
        print("❌ ALERT_CHANNEL_ID not found in .env file!")
        sys.exit(1)
    
    print("🚀 Starting Market Intelligence Bot...")
    bot.run(DISCORD_BOT_TOKEN)
