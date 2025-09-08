import logging
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
import pandas as pd

@dataclass
class ScraperConfig:
    base_url: str
    headers: Dict[str, str]
    timeout: int = 30
    max_retries: int = 3
    delay: float = 1.0

class BaseScraper(ABC):
    def __init__(self, domain: str):
        self.domain = domain
        self.config = self._load_config(domain)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        self.logger = logger.bind(scraper=self.__class__.__name__)
        
    def _load_config(self, domain: str) -> Dict[str, Any]:
        """Load configuration from data folder"""
        config_path = Path(f"data/{domain}/{domain}_url.json")
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        try:
            response = self.session.request(
                method, 
                url, 
                timeout=self.config.get('timeout', 30),
                **kwargs
            )
            response.raise_for_status()
            self.logger.info(f"Successfully fetched {url}")
            return response
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup"""
        return BeautifulSoup(html_content, 'lxml')
    
    @abstractmethod
    def scrape(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Main scraping method to be implemented by subclasses"""
        pass
    
    def save_data(self, data: List[Dict[str, Any]], filename: str):
        """Save scraped data in multiple formats"""
        output_dir = Path(f"outputs/scrapped_data/{self.domain}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame(data)
        
        # Save in multiple formats
        df.to_csv(output_dir / f"{filename}.csv", index=False)
        df.to_excel(output_dir / f"{filename}.xlsx", index=False)
        df.to_json(output_dir / f"{filename}.json", orient="records", indent=2)
        
        self.logger.info(f"Data saved to {output_dir}/{filename} in multiple formats")
    
    def __del__(self):
        """Cleanup session"""
        if hasattr(self, 'session'):
            self.session.close()