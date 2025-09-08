from typing import List, Dict, Any
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

class RealEstateScraper(BaseScraper):
    def __init__(self):
        super().__init__("real_estate")
    
    def scrape(self, max_pages: int = None) -> List[Dict[str, Any]]:
        """Scrape real estate data from multiple pages"""
        all_properties = []
        
        pages_to_scrape = max_pages or self.config.get('pages', 3)
        
        for page in range(1, pages_to_scrape + 1):
            url = f"{self.config['base_url']}homes/{page}_p/"
            response = self.make_request(url)
            
            if not response:
                continue
            
            soup = self.parse_html(response.text)
            properties = self._parse_properties_page(soup)
            all_properties.extend(properties)
            
            self.logger.info(f"Scraped page {page}: {len(properties)} properties")
            time.sleep(self.config.get('delay', 1.0))
        
        return all_properties
    
    def _parse_properties_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse a single page of properties"""
        properties = []
        selectors = self.config['selectors']
        property_elements = soup.select(selectors['property'])
        
        for prop_elem in property_elements:
            try:
                property_data = {
                    'price': self._extract_price(prop_elem, selectors['price']),
                    'address': self._extract_text(prop_elem, selectors['address']),
                    'details': self._extract_details(prop_elem, selectors['details']),
                    'agent': self._extract_text(prop_elem, selectors['agent']),
                    'url': f"{self.config['base_url']}{prop_elem.select_one('a').get('href', '') if prop_elem.select_one('a') else ''}",
                    'scraped_timestamp': pd.Timestamp.now()
                }
                properties.append(property_data)
            except Exception as e:
                self.logger.error(f"Error parsing property: {e}")
                continue
        
        return properties
    
    def _extract_text(self, elem, selector: str) -> str:
        selected = elem.select_one(selector)
        return selected.text.strip() if selected else "N/A"
    
    def _extract_price(self, elem, selector: str) -> str:
        price_elem = elem.select_one(selector)
        if price_elem:
            price_text = price_elem.text.strip()
            # Extract price information
            price_match = re.search(r'\$[\d,]+', price_text)
            return price_match.group(0) if price_match else "N/A"
        return "N/A"
    
    def _extract_details(self, elem, selector: str) -> str:
        details_elem = elem.select_one(selector)
        if details_elem:
            details = details_elem.select('li')
            return ", ".join([detail.text.strip() for detail in details]) if details else "N/A"
        return "N/A"