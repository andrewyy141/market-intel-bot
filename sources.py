# RSS Feed URLs
RSS_FEEDS = {
    'reuters_business': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best',
    'sec_press': 'https://www.sec.gov/news/pressreleases.rss',
    'fed_press': 'https://www.federalreserve.gov/feeds/press_all.xml',
}

# Google News RSS (per ticker - format: f"{base_url}TICKER+when:1d")
GOOGLE_NEWS_BASE = 'https://news.google.com/rss/search?q='

# Company IR RSS Feeds (major ones that publish RSS)
COMPANY_IR_FEEDS = {
    'AAPL': 'https://www.apple.com/newsroom/rss-feed.rss',
    'MSFT': 'https://news.microsoft.com/feed/',
    'NVDA': 'https://nvidianews.nvidia.com/releases.xml',
    # Add more as needed
}

# SEC CIK Mappings (for EDGAR API)
SEC_CIK_MAP = {
    'AAPL': '0000320193',
    'MSFT': '0000789019',
    'GOOGL': '0001652044',
    'AMZN': '0001018724',
    'NVDA': '0001045810',
    'META': '0001326801',
    'TSLA': '0001318605',
    'AMD': '0000002488',
    'INTC': '0000050863',
    'TSM': '0001046179',
    # Add more as needed
}

# FRED Series IDs (Economic Data)
FRED_SERIES = {
    'CPI': 'CPIAUCSL',
    'PCE': 'PCEPI',
    'UNEMPLOYMENT': 'UNRATE',
    'GDP': 'GDP',
    'FED_FUNDS': 'FEDFUNDS',
    'TREASURY_10Y': 'DGS10',
    'TREASURY_2Y': 'DGS2',
}

# Whitelisted Domains (only trust these)
WHITELISTED_DOMAINS = [
    'sec.gov',
    'federalreserve.gov',
    'reuters.com',
    'apple.com',
    'microsoft.com',
    'nvidia.com',
    'bls.gov',
    'bea.gov',
    'fred.stlouisfed.org'
]