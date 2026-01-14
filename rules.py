class RulesEngine:
    """Rules-based signal detection"""
    
    def evaluate(self, content, entities):
        """
        Evaluate content against rules
        Returns: dict with signal_type, category, confidence, context or None
        """
        
        source = content.get('source', '')
        text_lower = content.get('text', '').lower()
        
        # Rule 1: SEC 8-K Filings (Material Events)
        if source == 'SEC' and content.get('filing_type') == '8-K':
            category = content.get('category', 'Material Event')
            return {
                'signal_type': 'sec_filing',
                'category': f'Micro → {category}',
                'confidence': 0.95,
                'context': '8-K filing indicates material corporate event'
            }
        
        # Rule 2: Form 4 (Insider Trading)
        if source == 'SEC' and content.get('filing_type') == '4':
            return {
                'signal_type': 'insider_trade',
                'category': 'Micro → Management Action',
                'confidence': 0.90,
                'context': 'Insider transaction reported'
            }
        
        # Rule 3: FRED Macro Data
        if source == 'FRED':
            change_pct = content.get('change_pct', 0)
            series_name = content.get('series_name', '')
            
            if abs(change_pct) > 0.3:  # Significant change
                return {
                    'signal_type': 'macro_data',
                    'category': f'Macro → {series_name}',
                    'confidence': 0.85,
                    'context': f'{series_name} changed {change_pct:+.1f}%'
                }
        
        # Rule 4: Earnings Results
        if content.get('event_type') == 'earnings_result':
            surprise_pct = content.get('surprise_pct', 0)
            
            if abs(surprise_pct) >= 10:  # 10%+ surprise
                direction = 'Beat' if surprise_pct > 0 else 'Miss'
                return {
                    'signal_type': 'earnings',
                    'category': 'Micro → Earnings',
                    'confidence': 0.90,
                    'context': f'{direction} by {abs(surprise_pct):.1f}%'
                }
            elif abs(surprise_pct) >= 5:  # 5%+ surprise
                return {
                    'signal_type': 'earnings',
                    'category': 'Micro → Earnings',
                    'confidence': 0.80,
                    'context': f'Earnings surprise {surprise_pct:+.1f}%'
                }
        
        # Rule 5: M&A Activity
        if entities.get('event_type') == 'ma':
            if any(word in text_lower for word in ['acquires', 'acquisition', 'merger', 'acquired']):
                return {
                    'signal_type': 'ma_activity',
                    'category': 'Micro → Competition & M&A',
                    'confidence': 0.85,
                    'context': 'M&A activity detected'
                }
        
        # Rule 6: Management Changes
        if entities.get('event_type') == 'management':
            if any(word in text_lower for word in ['ceo', 'chief executive', 'president']):
                return {
                    'signal_type': 'management_change',
                    'category': 'Micro → Management Change',
                    'confidence': 0.85,
                    'context': 'Executive leadership change'
                }
        
        # Rule 7: Product Announcements (Company IR only)
        if 'IR' in source or source == 'Company IR':
            if any(word in text_lower for word in ['announces', 'launches', 'introduces', 'unveils']):
                return {
                    'signal_type': 'product_launch',
                    'category': 'Micro → Innovation',
                    'confidence': 0.80,
                    'context': 'New product/service announcement'
                }
        
        # Rule 8: Regulatory Action
        if entities.get('event_type') == 'regulatory':
            if any(word in text_lower for word in ['sec', 'ftc', 'investigation', 'lawsuit', 'settlement']):
                return {
                    'signal_type': 'regulatory',
                    'category': 'Micro → Regulation',
                    'confidence': 0.85,
                    'context': 'Regulatory action detected'
                }
        
        # Rule 9: Earnings Preview (upcoming)
        if content.get('event_type') == 'earnings':
            return {
                'signal_type': 'earnings_preview',
                'category': 'Micro → Earnings',
                'confidence': 0.75,
                'context': f"Earnings scheduled for {content.get('earnings_date', 'soon')}"
            }
        
        # No rules matched
        return None