from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

class SentimentAnalyzer:
    """Analyze sentiment using FinBERT (financial sentiment model)"""
    
    def __init__(self):
        try:
            # Use FinBERT for financial text
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                device=-1  # CPU only (free hosting)
            )
            self.enabled = True
            print("✅ FinBERT sentiment analyzer loaded")
        except Exception as e:
            print(f"⚠️  Could not load FinBERT: {e}")
            print("   Sentiment analysis will be disabled")
            self.enabled = False
    
    def analyze(self, text):
        """
        Analyze sentiment of text
        Returns: {'label': 'positive/negative/neutral', 'score': float}
        """
        if not self.enabled:
            return {'label': 'neutral', 'score': 0.5}
        
        try:
            # Truncate text to model's max length (512 tokens)
            text = text[:2000]  # Rough approximation
            
            result = self.sentiment_pipeline(text)[0]
            
            # FinBERT returns 'positive', 'negative', 'neutral'
            return {
                'label': result['label'].lower(),
                'score': result['score']
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {'label': 'neutral', 'score': 0.5}
    
    def get_sentiment_direction(self, text):
        """
        Simplified sentiment: BULLISH, BEARISH, or NEUTRAL
        """
        result = self.analyze(text)
        
        if result['score'] < 0.6:  # Low confidence
            return 'NEUTRAL'
        
        label = result['label']
        if label == 'positive':
            return 'BULLISH'
        elif label == 'negative':
            return 'BEARISH'
        else:
            return 'NEUTRAL'

# Global instance (loaded once at startup)
sentiment_analyzer = None

def get_sentiment_analyzer():
    """Get or create sentiment analyzer singleton"""
    global sentiment_analyzer
    if sentiment_analyzer is None:
        sentiment_analyzer = SentimentAnalyzer()
    return sentiment_analyzer