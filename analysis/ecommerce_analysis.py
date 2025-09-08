import pandas as pd
from .base_analysis import BaseAnalysis
from typing import Dict, Any
import re

class EcommerceAnalysis(BaseAnalysis):
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze e-commerce data and generate insights"""
        insights = {}
        
        # Basic statistics
        insights['total_products'] = len(data)
        
        # Price analysis
        prices = []
        for price_str in data['price']:
            if price_str != "N/A":
                numeric_price = re.sub(r'[^\d.]', '', price_str)
                if numeric_price:
                    prices.append(float(numeric_price))
        
        if prices:
            insights['avg_price'] = sum(prices) / len(prices)
            insights['min_price'] = min(prices)
            insights['max_price'] = max(prices)
        else:
            insights['avg_price'] = insights['min_price'] = insights['max_price'] = 0
        
        # Rating analysis
        ratings = []
        for rating_str in data['rating']:
            if rating_str != "N/A":
                numeric_rating = re.search(r'\d\.\d', rating_str)
                if numeric_rating:
                    ratings.append(float(numeric_rating.group()))
        
        if ratings:
            insights['avg_rating'] = sum(ratings) / len(ratings)
            insights['min_rating'] = min(ratings)
            insights['max_rating'] = max(ratings)
        else:
            insights['avg_rating'] = insights['min_rating'] = insights['max_rating'] = 0
        
        # Availability analysis
        availability_counts = data['availability'].value_counts().to_dict()
        insights['availability_distribution'] = availability_counts
        
        # Generate AI insights
        ai_insights = self._generate_ecommerce_insights(data, insights)
        insights['ai_analysis'] = ai_insights
        
        return insights
    
    def _generate_ecommerce_insights(self, data: pd.DataFrame, basic_stats: Dict) -> str:
        """Generate comprehensive AI insights about e-commerce data"""
        
        data_context = f"""
        E-commerce Data Analysis Context:
        - Total products analyzed: {basic_stats['total_products']}
        - Average price: ${basic_stats['avg_price']:.2f}
        - Price range: ${basic_stats['min_price']:.2f} - ${basic_stats['max_price']:.2f}
        - Average rating: {basic_stats['avg_rating']:.1f}/5
        - Availability: {basic_stats['availability_distribution']}
        """
        
        prompt = """
        Analyze this e-commerce dataset and provide insights on:
        1. Price competitiveness of products
        2. Relationship between price and rating
        3. Product availability trends
        4. Recommendations for buyers based on price and quality
        5. Market gaps and opportunities
        
        Format the response as a comprehensive e-commerce market analysis report.
        """
        
        return self.generate_ai_insights(prompt, data_context)