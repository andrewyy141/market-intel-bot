import re
from config.settings import WATCHLIST

def extract_ticker(text):
    """Extract ticker symbol from text"""
    text_upper = text.upper()
    
    # Try exact match first
    for ticker in WATCHLIST:
        pattern = r'\b' + re.escape(ticker) + r'\b'
        if re.search(pattern, text_upper):
            return ticker
    
    # Try company name mapping (common ones)
    company_names = {
        'APPLE': 'AAPL',
        'MICROSOFT': 'MSFT',
        'ALPHABET': 'GOOGL',
        'GOOGLE': 'GOOGL',
        'AMAZON': 'AMZN',
        'NVIDIA': 'NVDA',
        'META': 'META',
        'FACEBOOK': 'META',
        'TESLA': 'TSLA',
        'AMD': 'AMD',
        'INTEL': 'INTC',
        'TSMC': 'TSM',
        'TAIWAN SEMI': 'TSM',
    }
    
    for company, ticker in company_names.items():
        if company in text_upper and ticker in WATCHLIST:
            return ticker
    
    return None

def extract_numbers(text):
    """Extract financial numbers from text"""
    numbers = {}
    
    # Revenue patterns
    revenue_pattern = r'revenue[:\s]+\$?(\d+\.?\d*)\s*(billion|million|B|M)?'
    revenue_match = re.search(revenue_pattern, text, re.IGNORECASE)
    if revenue_match:
        value = float(revenue_match.group(1))
        unit = revenue_match.group(2)
        if unit and unit.upper() in ['BILLION', 'B']:
            value *= 1_000_000_000
        elif unit and unit.upper() in ['MILLION', 'M']:
            value *= 1_000_000
        numbers['revenue'] = value
    
    # EPS patterns
    eps_pattern = r'EPS[:\s]+\$?(\d+\.?\d*)'
    eps_match = re.search(eps_pattern, text, re.IGNORECASE)
    if eps_match:
        numbers['eps'] = float(eps_match.group(1))
    
    # Percentage patterns
    pct_pattern = r'(\d+\.?\d*)%'
    pct_matches = re.findall(pct_pattern, text)
    if pct_matches:
        numbers['percentages'] = [float(p) for p in pct_matches]
    
    return numbers

def extract_entities(text):
    """Extract key entities (simplified without spaCy for now)"""
    entities = {
        'ticker': extract_ticker(text),
        'numbers': extract_numbers(text),
    }
    
    # Detect event types
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['earnings', 'revenue', 'eps', 'profit']):
        entities['event_type'] = 'earnings'
    elif any(word in text_lower for word in ['acquisition', 'merger', 'acquired', 'bought']):
        entities['event_type'] = 'ma'
    elif any(word in text_lower for word in ['ceo', 'cfo', 'executive', 'appointment', 'departure']):
        entities['event_type'] = 'management'
    elif any(word in text_lower for word in ['product', 'launch', 'release', 'announced']):
        entities['event_type'] = 'product'
    elif any(word in text_lower for word in ['regulation', 'sec', 'ftc', 'investigation']):
        entities['event_type'] = 'regulatory'
    else:
        entities['event_type'] = 'general'
    
    return entities