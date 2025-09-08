from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd
from pathlib import Path
from loguru import logger
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAnalysis(ABC):
    def __init__(self):
        self.logger = logger.bind(analysis=self.__class__.__name__)
        openai.api_key = os.getenv('OPENAI_API_KEY')
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Main analysis method to be implemented by subclasses"""
        pass
    
    def generate_ai_insights(self, prompt: str, data_context: str = "") -> str:
        """Generate AI insights using OpenAI GPT"""
        try:
            full_prompt = f"""
            {data_context}
            
            {prompt}
            
            Please provide comprehensive, data-driven insights in markdown format.
            Include specific findings, trends, and actionable recommendations.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a data analysis expert. Provide detailed insights in markdown format."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return f"AI analysis failed: {str(e)}"
    
    def save_report(self, insights: str, domain: str, report_name: str):
        """Save analysis report"""
        report_dir = Path(f"outputs/report")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / f"{domain}_{report_name}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(insights)
        
        self.logger.info(f"Report saved to {report_path}")