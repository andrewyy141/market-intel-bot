from fredapi import Fred
from datetime import datetime, timedelta
from config.settings import FRED_API_KEY
from config.sources import FRED_SERIES

class FREDIngestor:
    """Ingest economic data from FRED API"""
    
    def __init__(self):
        if FRED_API_KEY:
            self.fred = Fred(api_key=FRED_API_KEY)
        else:
            self.fred = None
            print("⚠️  FRED API key not found - macro data disabled")
    
    async def get_recent_data(self, hours=24):
        """Get recent economic data releases"""
        if not self.fred:
            return []
        
        data_points = []
        cutoff_date = datetime.now() - timedelta(hours=hours)
        
        for series_name, series_id in FRED_SERIES.items():
            try:
                # Get latest observation
                series_data = self.fred.get_series(series_id, observation_start=cutoff_date.date())
                
                if series_data.empty:
                    continue
                
                latest_value = series_data.iloc[-1]
                latest_date = series_data.index[-1]
                
                # Calculate change if we have previous data
                change = None
                change_pct = None
                if len(series_data) > 1:
                    prev_value = series_data.iloc[-2]
                    change = latest_value - prev_value
                    if prev_value != 0:
                        change_pct = (change / prev_value) * 100
                
                data_point = {
                    'source': 'FRED',
                    'series_name': series_name,
                    'series_id': series_id,
                    'value': latest_value,
                    'timestamp': datetime.combine(latest_date, datetime.min.time()),
                    'change': change,
                    'change_pct': change_pct,
                    'text': f"{series_name}: {latest_value:.2f}" + 
                           (f" (change: {change:+.2f})" if change else ""),
                    'url': f"https://fred.stlouisfed.org/series/{series_id}"
                }
                
                data_points.append(data_point)
                
            except Exception as e:
                print(f"Error fetching FRED series {series_name}: {e}")
                continue
        
        return data_points
    
    def is_significant_change(self, data_point):
        """Determine if economic data change is significant"""
        series_name = data_point['series_name']
        change_pct = data_point.get('change_pct')
        
        if change_pct is None:
            return False
        
        # Thresholds for significance (customizable)
        thresholds = {
            'CPI': 0.3,           # 0.3% monthly change
            'PCE': 0.3,
            'UNEMPLOYMENT': 0.2,  # 0.2 percentage points
            'FED_FUNDS': 0.1,     # 0.1 percentage points (10 bps)
            'TREASURY_10Y': 5,    # 5% change in yield
            'TREASURY_2Y': 5,
            'GDP': 0.5            # 0.5% quarterly change
        }
        
        threshold = thresholds.get(series_name, 1.0)
        return abs(change_pct) >= threshold