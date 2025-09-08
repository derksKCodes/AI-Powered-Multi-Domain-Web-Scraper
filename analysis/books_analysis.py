import pandas as pd
from .base_analysis import BaseAnalysis
from typing import Dict, Any

class BooksAnalysis(BaseAnalysis):
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze books data and generate insights"""
        insights = {}
        
        # Basic statistics
        insights['total_books'] = len(data)
        insights['avg_price'] = data['price'].mean()
        insights['price_range'] = (data['price'].min(), data['price'].max())
        
        # Rating distribution
        rating_counts = data['rating'].value_counts().to_dict()
        insights['rating_distribution'] = rating_counts
        
        # Price analysis by rating
        price_by_rating = data.groupby('rating')['price'].agg(['mean', 'min', 'max']).to_dict()
        insights['price_by_rating'] = price_by_rating
        
        # Generate AI insights
        ai_insights = self._generate_book_insights(data, insights)
        insights['ai_analysis'] = ai_insights
        
        return insights
    
    def _generate_book_insights(self, data: pd.DataFrame, basic_stats: Dict) -> str:
        """Generate comprehensive AI insights about books data"""
        
        data_context = f"""
        Books Data Analysis Context:
        - Total books analyzed: {basic_stats['total_books']}
        - Average price: ${basic_stats['avg_price']:.2f}
        - Price range: ${basic_stats['price_range'][0]:.2f} - ${basic_stats['price_range'][1]:.2f}
        - Rating distribution: {basic_stats['rating_distribution']}
        """
        
        prompt = """
        Analyze this books dataset and provide insights on:
        1. Which genres/rating categories offer the best value (lowest price for highest rating)?
        2. Price distribution patterns across different rating levels
        3. Recommendations for book buyers based on price vs quality
        4. Any interesting trends or patterns in the data
        5. Potential market opportunities or gaps
        
        Format the response as a comprehensive market analysis report.
        """
        
        return self.generate_ai_insights(prompt, data_context)