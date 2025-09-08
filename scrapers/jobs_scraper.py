from typing import List, Dict, Any
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

class JobsScraper(BaseScraper):
    def __init__(self):
        super().__init__("jobs")
    
    def scrape(self, max_pages: int = None) -> List[Dict[str, Any]]:
        """Scrape jobs data from multiple pages"""
        all_jobs = []
        
        pages_to_scrape = max_pages or self.config.get('pages', 3)
        
        for page in range(1, pages_to_scrape + 1):
            url = f"{self.config['base_url']}remote-dev-jobs/{page}"
            response = self.make_request(url)
            
            if not response:
                continue
            
            soup = self.parse_html(response.text)
            jobs = self._parse_jobs_page(soup)
            all_jobs.extend(jobs)
            
            self.logger.info(f"Scraped page {page}: {len(jobs)} jobs")
            time.sleep(self.config.get('delay', 1.0))
        
        return all_jobs
    
    def _parse_jobs_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse a single page of jobs"""
        jobs = []
        selectors = self.config['selectors']
        job_elements = soup.select(selectors['job'])
        
        for job_elem in job_elements:
            try:
                job = {
                    'title': self._extract_text(job_elem, selectors['title']),
                    'company': self._extract_text(job_elem, selectors['company']),
                    'tags': self._extract_tags(job_elem, selectors['tags']),
                    'location': self._extract_text(job_elem, selectors['location']),
                    'salary': self._extract_salary(job_elem, selectors['salary']),
                    'url': f"{self.config['base_url']}{job_elem.get('data-url', '')}",
                    'scraped_timestamp': pd.Timestamp.now()
                }
                jobs.append(job)
            except Exception as e:
                self.logger.error(f"Error parsing job: {e}")
                continue
        
        return jobs
    
    def _extract_text(self, elem, selector: str) -> str:
        selected = elem.select_one(selector)
        return selected.text.strip() if selected else "N/A"
    
    def _extract_tags(self, elem, selector: str) -> str:
        tags = elem.select(selector)
        return ", ".join([tag.text.strip() for tag in tags]) if tags else "N/A"
    
    def _extract_salary(self, elem, selector: str) -> str:
        salary_elem = elem.select_one(selector)
        if salary_elem:
            salary_text = salary_elem.text.strip()
            # Look for salary patterns
            salary_match = re.search(r'\$[\d,]+(?:\.\d{2})?(?:\s*-\s*\$[\d,]+(?:\.\d{2})?)?', salary_text)
            return salary_match.group(0) if salary_match else "N/A"
        return "N/A"