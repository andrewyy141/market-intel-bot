import feedparser
from datetime import datetime, timedelta
from config.sources import RSS_FEEDS, COMPANY_IR_FEEDS, GOOGLE_NEWS_BASE
from config.settings import WATCHLIST
import re

class RSSIngestor:
    """Ingest news from RSS feeds"""
    
    async def get_recent_news(self, hours=24):
        """Fetch recent news from all RSS sources"""
        all_news = []
        
        # General news feeds
        for source_name, feed_url in RSS_FEEDS.items():
            news = await self._parse_feed(feed_url, source_name, hours)
            all_news.extend(news)
        
        # Company IR feeds
        for ticker, feed_url in COMPANY_IR_FEEDS.items():
            news = await self._parse_feed(feed_url, f'{ticker}_IR', hours)
            for item in news:
                item['ticker'] = ticker
            all_news.extend(news)
        
        # Google News (per ticker)
        for ticker in WATCHLIST[:5]:  # Limit to avoid rate limits
            news = await self._get_google_news(ticker, hours)
            all_news.extend(news)
        
        return all_news
    
    async def _parse_feed(self, feed_url, source_name, hours):
        """Parse RSS feed and return recent entries"""
        try:
            feed = feedparser.parse(feed_url)
            recent_news = []
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            for entry in feed.entries:
                # Parse publish date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                else:
                    pub_date = datetime.now()
                
                if pub_date < cutoff_time:
                    continue
                
                # Extract content
                content = entry.get('summary', entry.get('description', ''))
                
                news_item = {
                    'source': source_name,
                    'title': entry.title,
                    'url': entry.link,
                    'timestamp': pub_date,
                    'text': f"{entry.title} - {content}",
                    'ticker': self._extract_ticker(entry.title + ' ' + content)
                }
                
                recent_news.append(news_item)
            
            return recent_news
            
        except Exception as e:
            print(f"Error parsing feed {source_name}: {e}")
            return []
    
    async def _get_google_news(self, ticker, hours):
        """Get Google News for specific ticker"""
        try:
            query = f"{ticker} stock when:1d"
            feed_url = GOOGLE_NEWS_BASE + query.replace(' ', '+')
            
            feed = feedparser.parse(feed_url)
            recent_news = []
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            for entry in feed.entries[:5]:  # Limit to top 5
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                else:
                    pub_date = datetime.now()
                
                if pub_date < cutoff_time:
                    continue
                
                news_item = {
                    'source': 'Google News',
                    'ticker': ticker,
                    'title': entry.title,
                    'url': entry.link,
                    'timestamp': pub_date,
                    'text': entry.title + ' ' + entry.get('summary', '')
                }
                
                recent_news.append(news_item)
            
            return recent_news
            
        except Exception as e:
            print(f"Error getting Google News for {ticker}: {e}")
            return []
    
    def _extract_ticker(self, text):
        """Extract ticker symbol from text"""
        text_upper = text.upper()
        
        for ticker in WATCHLIST:
            # Look for ticker as standalone word
            pattern = r'\b' + re.escape(ticker) + r'\b'
            if re.search(pattern, text_upper):
                return ticker
        
        return None