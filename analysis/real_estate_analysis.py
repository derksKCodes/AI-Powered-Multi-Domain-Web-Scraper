import pandas as pd
from .base_analysis import BaseAnalysis
from typing import Dict, Any
import re

class RealEstateAnalysis(BaseAnalysis):
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze real estate data and generate insights"""
        insights = {}
        
        # Basic statistics
        insights['total_properties'] = len(data)
        
        # Extract numeric prices
        prices = []
        for price_str in data['price']:
            if price_str != "N/A":
                numeric_price = re.sub(r'[^\d]', '', price_str)
                if numeric_price:
                    prices.append(float(numeric_price))
        
        if prices:
            insights['avg_price'] = sum(prices) / len(prices)
            insights['min_price'] = min(prices)
            insights['max_price'] = max(prices)
        else:
            insights['avg_price'] = insights['min_price'] = insights['max_price'] = 0
        
        # Location analysis (from addresses)
        locations = []
        for address in data['address']:
            if address != "N/A":
                # Extract city/state from address
                parts = address.split(',')
                if len(parts) >= 2:
                    locations.append(parts[-2].strip() + ', ' + parts[-1].strip())
        
        location_counts = pd.Series(locations).value_counts().to_dict()
        insights['location_distribution'] = location_counts
        
        # Generate AI insights
        ai_insights = self._generate_real_estate_insights(data, insights)
        insights['ai_analysis'] = ai_insights
        
        return insights
    
    def _generate_real_estate_insights(self, data: pd.DataFrame, basic_stats: Dict) -> str:
        """Generate comprehensive AI insights about real estate data"""
        
        data_context = f"""
        Real Estate Data Analysis Context:
        - Total properties analyzed: {basic_stats['total_properties']}
        - Average price: ${basic_stats['avg_price']:,.2f}
        - Price range: ${basic_stats['min_price']:,.2f} - ${basic_stats['max_price']:,.2f}
        - Top locations: {dict(list(basic_stats['location_distribution'].items())[:5])}
        """
        
        prompt = """
        Analyze this real estate dataset and provide insights on:
        1. Price trends in different locations
        2. Most affordable vs most expensive areas
        3. Recommendations for buyers based on location and price
        4. Any emerging real estate market trends
        5. Investment opportunities in different areas
        
        Format the response as a comprehensive real estate market analysis report.
        """
        
        return self.generate_ai_insights(prompt, data_context)