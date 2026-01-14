import hashlib
from urllib.parse import urlparse
from config.settings import TRUSTED_SOURCES, SPONSORED_KEYWORDS, OPINION_URL_PATTERNS
from config.sources import WHITELISTED_DOMAINS
from database.models import is_duplicate, cache_content

class ContentValidator:
    """Validate content quality and filter out ads/opinions"""
    
    async def is_valid(self, content):
        """
        Multi-stage validation pipeline
        Returns: (is_valid: bool, reason: str)
        """
        
        # Stage 1: Source whitelist check
        source = content.get('source', '')
        if source and source not in TRUSTED_SOURCES and source != 'Google News':
            # Google News gets special handling since it aggregates
            if 'IR' not in source:  # Company IR sources are trusted
                return False, f"Untrusted source: {source}"
        
        # Stage 2: URL domain whitelist
        url = content.get('url', '')
        if url:
            domain = urlparse(url).netloc.lower()
            domain = domain.replace('www.', '')
            
            # Check if domain is whitelisted or is a known company
            is_whitelisted = any(
                whitelisted in domain 
                for whitelisted in WHITELISTED_DOMAINS
            )
            
            if not is_whitelisted and source != 'Google News':
                return False, f"Non-whitelisted domain: {domain}"
        
        # Stage 3: Duplicate detection
        text = content.get('text', content.get('title', ''))
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        
        if await is_duplicate(content_hash):
            return False, "Duplicate content"
        
        # Stage 4: Sponsored content keywords
        text_lower = text.lower()
        for keyword in SPONSORED_KEYWORDS:
            if keyword in text_lower:
                return False, f"Contains sponsored keyword: {keyword}"
        
        # Stage 5: Opinion URL patterns
        if url:
            for pattern in OPINION_URL_PATTERNS:
                if pattern in url.lower():
                    return False, f"Opinion URL pattern: {pattern}"
        
        # Stage 6: Opinion language detection (simple keyword approach)
        opinion_indicators = [
            'i think', 'i believe', 'in my opinion', 'we believe',
            'could', 'might', 'may', 'should',
            'overvalued', 'undervalued', 'likely to',
            'prediction', 'forecast', 'expect'
        ]
        
        opinion_count = sum(1 for indicator in opinion_indicators if indicator in text_lower)
        if opinion_count >= 3:  # Multiple opinion indicators
            return False, "Contains opinion language"
        
        # Stage 7: Ticker relevance (only for news items)
        if source in ['Google News', 'Reuters'] and not content.get('ticker'):
            # Try to extract ticker from text
            from processing.extractor import extract_ticker
            ticker = extract_ticker(text)
            if not ticker:
                return False, "No relevant ticker found"
            content['ticker'] = ticker
        
        # Passed all checks - cache it
        await cache_content(content_hash, content.get('ticker'), source)
        
        return True, "Valid"
    
    def is_factual_language(self, text):
        """Check if text uses factual language vs opinion"""
        factual_indicators = [
            'reported', 'announced', 'filed', 'released',
            'according to', 'data shows', 'statistics',
            'earnings', 'revenue', 'results'
        ]
        
        text_lower = text.lower()
        factual_count = sum(1 for indicator in factual_indicators if indicator in text_lower)
        
        return factual_count >= 2