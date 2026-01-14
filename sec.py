import requests
import feedparser
from datetime import datetime, timedelta
from config.settings import WATCHLIST
from config.sources import SEC_CIK_MAP

class SECIngestor:
    """Ingest SEC filings for watched tickers"""
    
    def __init__(self):
        self.base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        self.headers = {
            'User-Agent': 'MarketIntelBot/1.0 (your-email@example.com)'
        }
    
    async def get_recent_filings(self, hours=24):
        """Get recent 8-K and Form 4 filings for watchlist"""
        filings = []
        
        for ticker in WATCHLIST:
            if ticker not in SEC_CIK_MAP:
                continue
            
            cik = SEC_CIK_MAP[ticker]
            
            # Get 8-K filings (material events)
            filings_8k = await self._fetch_filing_type(ticker, cik, '8-K', hours)
            filings.extend(filings_8k)
            
            # Get Form 4 filings (insider trades)
            filings_form4 = await self._fetch_filing_type(ticker, cik, '4', hours)
            filings.extend(filings_form4)
        
        return filings
    
    async def _fetch_filing_type(self, ticker, cik, filing_type, hours):
        """Fetch specific filing type for a ticker"""
        try:
            params = {
                'action': 'getcompany',
                'CIK': cik,
                'type': filing_type,
                'dateb': '',
                'owner': 'exclude',
                'count': '10',
                'output': 'atom'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            feed = feedparser.parse(response.text)
            recent_filings = []
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            for entry in feed.entries:
                filing_date = datetime(*entry.updated_parsed[:6])
                
                if filing_date < cutoff_time:
                    continue
                
                filing = {
                    'ticker': ticker,
                    'source': 'SEC',
                    'filing_type': filing_type,
                    'title': entry.title,
                    'summary': entry.summary,
                    'url': entry.link,
                    'timestamp': filing_date,
                    'text': f"{entry.title} - {entry.summary}"
                }
                
                recent_filings.append(filing)
            
            return recent_filings
            
        except Exception as e:
            print(f"Error fetching {filing_type} for {ticker}: {e}")
            return []

    def parse_8k_content(self, filing):
        """Extract key info from 8-K filing"""
        summary = filing.get('summary', '').lower()
        
        # Common 8-K items
        if 'item 2.02' in summary or 'results of operations' in summary:
            filing['category'] = 'Earnings'
        elif 'item 1.01' in summary or 'material definitive agreement' in summary:
            filing['category'] = 'Material Contract'
        elif 'item 5.02' in summary or 'departure' in summary or 'appointment' in summary:
            filing['category'] = 'Management Change'
        elif 'item 8.01' in summary:
            filing['category'] = 'Other Event'
        else:
            filing['category'] = 'Material Event'
        
        return filing