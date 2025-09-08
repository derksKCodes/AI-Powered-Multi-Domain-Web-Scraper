import pandas as pd
from .base_analysis import BaseAnalysis
from typing import Dict, Any
import re

class JobsAnalysis(BaseAnalysis):
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze jobs data and generate insights"""
        insights = {}
        
        # Basic statistics
        insights['total_jobs'] = len(data)
        
        # Company distribution
        company_counts = data['company'].value_counts().to_dict()
        insights['company_distribution'] = company_counts
        
        # Location analysis
        location_counts = data['location'].value_counts().to_dict()
        insights['location_distribution'] = location_counts
        
        # Skills/tags analysis
        all_tags = []
        for tags in data['tags']:
            if tags != "N/A":
                all_tags.extend([tag.strip() for tag in tags.split(',')])
        
        tag_counts = pd.Series(all_tags).value_counts().to_dict()
        insights['top_skills'] = dict(list(tag_counts.items())[:10])
        
        # Generate AI insights
        ai_insights = self._generate_jobs_insights(data, insights)
        insights['ai_analysis'] = ai_insights
        
        return insights
    
    def _generate_jobs_insights(self, data: pd.DataFrame, basic_stats: Dict) -> str:
        """Generate comprehensive AI insights about jobs data"""
        
        data_context = f"""
        Jobs Data Analysis Context:
        - Total jobs analyzed: {basic_stats['total_jobs']}
        - Top companies: {dict(list(basic_stats['company_distribution'].items())[:5])}
        - Top locations: {dict(list(basic_stats['location_distribution'].items())[:5])}
        - Top skills in demand: {basic_stats['top_skills']}
        """
        
        prompt = """
        Analyze this jobs dataset and provide insights on:
        1. Which skills are most in demand in the current job market?
        2. Which companies are hiring the most?
        3. What are the most common job locations?
        4. Recommendations for job seekers based on skills in demand
        5. Any emerging trends in the job market
        
        Format the response as a comprehensive job market analysis report.
        """
        
        return self.generate_ai_insights(prompt, data_context)