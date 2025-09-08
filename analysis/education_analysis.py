import pandas as pd
from .base_analysis import BaseAnalysis
from typing import Dict, Any
import re

class EducationAnalysis(BaseAnalysis):
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze education data and generate insights"""
        insights = {}
        
        # Basic statistics
        insights['total_courses'] = len(data)
        
        # Instructor analysis
        instructor_counts = data['instructor'].value_counts().to_dict()
        insights['instructor_distribution'] = instructor_counts
        
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
        
        # Duration analysis
        duration_counts = data['duration'].value_counts().to_dict()
        insights['duration_distribution'] = duration_counts
        
        # Generate AI insights
        ai_insights = self._generate_education_insights(data, insights)
        insights['ai_analysis'] = ai_insights
        
        return insights
    
    def _generate_education_insights(self, data: pd.DataFrame, basic_stats: Dict) -> str:
        """Generate comprehensive AI insights about education data"""
        
        data_context = f"""
        Education Data Analysis Context:
        - Total courses analyzed: {basic_stats['total_courses']}
        - Average rating: {basic_stats['avg_rating']:.1f}/5
        - Rating range: {basic_stats['min_rating']:.1f} - {basic_stats['max_rating']:.1f}
        - Top instructors: {dict(list(basic_stats['instructor_distribution'].items())[:5])}
        - Course durations: {dict(list(basic_stats['duration_distribution'].items())[:5])}
        """
        
        prompt = """
        Analyze this education dataset and provide insights on:
        1. Course quality based on ratings
        2. Most popular instructors
        3. Common course durations
        4. Recommendations for learners based on course quality
        5. Trends in online education
        
        Format the response as a comprehensive education market analysis report.
        """
        
        return self.generate_ai_insights(prompt, data_context)