import discord
from datetime import datetime

class AlertFormatter:
    """Format signals as Discord embeds"""
    
    @staticmethod
    def format_signal(signal):
        """Create Discord embed for signal"""
        
        # Determine color based on signal type
        color = AlertFormatter._get_color(signal)
        
        # Determine emoji
        emoji = AlertFormatter._get_emoji(signal)
        
        # Create embed
        embed = discord.Embed(
            title=f"{emoji} {signal['ticker']} - {signal['signal_type'].replace('_', ' ').title()}",
            description=signal['headline'],
            color=color,
            timestamp=signal['timestamp']
        )
        
        # Add category field
        embed.add_field(
            name="📊 Category",
            value=signal['category'],
            inline=True
        )
        
        # Add confidence field
        confidence_emoji = "🟢" if signal['confidence'] >= 0.9 else "🟡"
        embed.add_field(
            name=f"{confidence_emoji} Confidence",
            value=f"{signal['confidence']:.0%}",
            inline=True
        )
        
        # Add sentiment if available
        if signal.get('sentiment'):
            sentiment_emoji = {
                'BULLISH': '📈',
                'BEARISH': '📉',
                'NEUTRAL': '➡️'
            }.get(signal['sentiment'], '➡️')
            
            embed.add_field(
                name=f"{sentiment_emoji} Sentiment",
                value=signal['sentiment'],
                inline=True
            )
        
        # Add details
        if signal.get('details'):
            embed.add_field(
                name="💡 Details",
                value=signal['details'][:1024],  # Discord limit
                inline=False
            )
        
        # Add source link
        if signal.get('source_url'):
            embed.add_field(
                name="🔗 Source",
                value=f"[View Full Document]({signal['source_url']})",
                inline=False
            )
        
        # Footer
        embed.set_footer(
            text=f"Market Intelligence Bot • {datetime.now().strftime('%I:%M %p ET')}"
        )
        
        return embed
    
    @staticmethod
    def _get_color(signal):
        """Get embed color based on signal type"""
        colors = {
            'sec_filing': discord.Color.red(),
            'insider_trade': discord.Color.orange(),
            'macro_data': discord.Color.blue(),
            'earnings': discord.Color.gold(),
            'ma_activity': discord.Color.purple(),
            'management_change': discord.Color.orange(),
            'product_launch': discord.Color.green(),
            'regulatory': discord.Color.dark_red(),
            'earnings_preview': discord.Color.light_grey()
        }
        return colors.get(signal['signal_type'], discord.Color.blurple())
    
    @staticmethod
    def _get_emoji(signal):
        """Get emoji based on signal type"""
        emojis = {
            'sec_filing': '🔴',
            'insider_trade': '💼',
            'macro_data': '📊',
            'earnings': '💰',
            'ma_activity': '🤝',
            'management_change': '👔',
            'product_launch': '🚀',
            'regulatory': '⚖️',
            'earnings_preview': '📅'
        }
        return emojis.get(signal['signal_type'], '📢')
    
    @staticmethod
    def format_daily_summary(signals):
        """Create daily summary embed"""
        embed = discord.Embed(
            title="📋 Daily Signal Summary",
            description=f"Detected {len(signals)} signals today",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # Group by ticker
        by_ticker = {}
        for signal in signals:
            ticker = signal['ticker']
            if ticker not in by_ticker:
                by_ticker[ticker] = []
            by_ticker[ticker].append(signal)
        
        # Add field for each ticker
        for ticker, ticker_signals in list(by_ticker.items())[:10]:  # Max 10 tickers
            signal_types = [s['signal_type'].replace('_', ' ').title() for s in ticker_signals]
            embed.add_field(
                name=f"{ticker} ({len(ticker_signals)} signals)",
                value=', '.join(signal_types[:3]),  # Max 3 types
                inline=False
            )
        
        return embed