import yfinance as yf
from datetime import datetime, timedelta
from config.settings import WATCHLIST

class YahooFinanceIngestor:
    """Ingest earnings and price data from Yahoo Finance"""
    
    async def get_earnings_data(self):
        """Get upcoming and recent earnings for watchlist"""
        earnings_events = []
        
        for ticker in WATCHLIST:
            try:
                stock = yf.Ticker(ticker)
                
                # Get earnings dates
                calendar = stock.calendar
                if calendar is None or calendar.empty:
                    continue
                
                # Check if earnings are within next 7 days or past 24 hours
                earnings_date = calendar.get('Earnings Date')
                if earnings_date is not None and len(earnings_date) > 0:
                    earnings_date = earnings_date[0]
                    
                    now = datetime.now()
                    days_until = (earnings_date - now).days
                    
                    if -1 <= days_until <= 7:  # Past 24h or next 7 days
                        event = {
                            'source': 'Yahoo Finance',
                            'ticker': ticker,
                            'event_type': 'earnings',
                            'earnings_date': earnings_date,
                            'timestamp': now,
                            'text': f"{ticker} earnings on {earnings_date.strftime('%Y-%m-%d')}",
                            'url': f"https://finance.yahoo.com/quote/{ticker}"
                        }
                        earnings_events.append(event)
                
                # Get recent earnings results if available
                earnings_history = stock.earnings_history
                if earnings_history is not None and not earnings_history.empty:
                    latest = earnings_history.iloc[0]
                    
                    # Check if within last 48 hours
                    earnings_date = latest.name
                    if isinstance(earnings_date, str):
                        earnings_date = datetime.strptime(earnings_date, '%Y-%m-%d')
                    
                    hours_since = (datetime.now() - earnings_date).total_seconds() / 3600
                    
                    if hours_since <= 48:
                        eps_actual = latest.get('epsActual', 0)
                        eps_estimate = latest.get('epsEstimate', 0)
                        surprise_pct = 0
                        
                        if eps_estimate != 0:
                            surprise_pct = ((eps_actual - eps_estimate) / abs(eps_estimate)) * 100
                        
                        result = {
                            'source': 'Yahoo Finance',
                            'ticker': ticker,
                            'event_type': 'earnings_result',
                            'eps_actual': eps_actual,
                            'eps_estimate': eps_estimate,
                            'surprise_pct': surprise_pct,
                            'timestamp': earnings_date,
                            'text': f"{ticker} earnings: ${eps_actual:.2f} vs ${eps_estimate:.2f} est ({surprise_pct:+.1f}%)",
                            'url': f"https://finance.yahoo.com/quote/{ticker}"
                        }
                        earnings_events.append(result)
                        
            except Exception as e:
                print(f"Error fetching Yahoo data for {ticker}: {e}")
                continue
        
        return earnings_events
    
    async def get_price_data(self, ticker):
        """Get recent price data for a ticker"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='5d')
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else latest
            
            price_change = latest['Close'] - prev['Close']
            price_change_pct = (price_change / prev['Close']) * 100
            
            return {
                'ticker': ticker,
                'price': latest['Close'],
                'change': price_change,
                'change_pct': price_change_pct,
                'volume': latest['Volume']
            }
            
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
            return None