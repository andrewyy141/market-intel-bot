from datetime import datetime
from signals.rules import RulesEngine
from processing.extractor import extract_entities
from processing.sentiment import get_sentiment_analyzer
from config.settings import MIN_CONFIDENCE

class SignalDetector:
    """Main signal detection engine"""
    
    def __init__(self):
        self.rules = RulesEngine()
        self.sentiment_analyzer = get_sentiment_analyzer()
    
    async def detect(self, content):
        """
        Detect if content contains a tradeable signal
        Returns: Signal dict or None
        """
        
        # Extract structured info
        entities = extract_entities(content.get('text', ''))
        ticker = content.get('ticker') or entities.get('ticker')
        
        if not ticker:
            return None
        
        # Run rules engine
        rule_result = self.rules.evaluate(content, entities)
        
        if not rule_result:
            return None
        
        # Calculate confidence
        base_confidence = rule_result['confidence']
        
        # Boost confidence for trusted sources
        if content.get('source') in ['SEC', 'FRED', 'Company IR']:
            base_confidence *= 1.1
        
        # Apply sentiment analysis
        sentiment = self.sentiment_analyzer.get_sentiment_direction(content.get('text', ''))
        
        final_confidence = min(base_confidence, 1.0)
        
        # Threshold check
        if final_confidence < MIN_CONFIDENCE:
            return None
        
        # Build signal
        signal = {
            'ticker': ticker,
            'signal_type': rule_result['signal_type'],
            'category': rule_result['category'],
            'headline': self._generate_headline(content, entities),
            'details': self._generate_details(content, entities, rule_result),
            'confidence': final_confidence,
            'timestamp': content.get('timestamp', datetime.now()),
            'source_url': content.get('url', ''),
            'is_opinion': False,
            'sentiment': sentiment
        }
        
        return signal
    
    def _generate_headline(self, content, entities):
        """Generate concise headline for alert"""
        title = content.get('title', '')
        
        # Clean up title
        if len(title) > 100:
            title = title[:97] + '...'
        
        return title
    
    def _generate_details(self, content, entities, rule_result):
        """Generate detailed explanation"""
        details = []
        
        # Add key numbers if available
        numbers = entities.get('numbers', {})
        if 'revenue' in numbers:
            details.append(f"Revenue: ${numbers['revenue']/1e9:.1f}B")
        if 'eps' in numbers:
            details.append(f"EPS: ${numbers['eps']:.2f}")
        
        # Add rule-specific context
        if rule_result.get('context'):
            details.append(rule_result['context'])
        
        # Add text summary (first 200 chars)
        text = content.get('text', content.get('summary', ''))
        if text:
            summary = text[:200]
            if len(text) > 200:
                summary += '...'
            details.append(summary)
        
        return ' | '.join(details) if details else text[:300]