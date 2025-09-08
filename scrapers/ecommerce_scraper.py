from typing import List, Dict, Any
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

class EcommerceScraper(BaseScraper):
    def __init__(self):
        super().__init__("ecommerce")
    
    def scrape(self, max_pages: int = None, search_term: str = "laptop") -> List[Dict[str, Any]]:
        """Scrape e-commerce data from multiple pages"""
        all_products = []
        
        pages_to_scrape = max_pages or self.config.get('pages', 3)
        
        for page in range(1, pages_to_scrape + 1):
            url = f"{self.config['base_url']}s?k={search_term}&page={page}"
            response = self.make_request(url)
            
            if not response:
                continue
            
            soup = self.parse_html(response.text)
            products = self._parse_products_page(soup)
            all_products.extend(products)
            
            self.logger.info(f"Scraped page {page}: {len(products)} products")
            time.sleep(self.config.get('delay', 1.0))
        
        return all_products
    
    def _parse_products_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse a single page of products"""
        products = []
        selectors = self.config['selectors']
        product_elements = soup.select(selectors['product'])
        
        for product_elem in product_elements:
            try:
                product = {
                    'name': self._extract_text(product_elem, selectors['name']),
                    'price': self._extract_price(product_elem, selectors['price']),
                    'rating': self._extract_rating(product_elem, selectors['rating']),
                    'availability': self._extract_text(product_elem, selectors['availability']),
                    'url': f"{self.config['base_url']}{product_elem.select_one('a').get('href', '') if product_elem.select_one('a') else ''}",
                    'scraped_timestamp': pd.Timestamp.now()
                }
                products.append(product)
            except Exception as e:
                self.logger.error(f"Error parsing product: {e}")
                continue
        
        return products
    
    def _extract_text(self, elem, selector: str) -> str:
        selected = elem.select_one(selector)
        return selected.text.strip() if selected else "N/A"
    
    def _extract_price(self, elem, selector: str) -> str:
        price_elem = elem.select_one(selector)
        if price_elem:
            price_text = price_elem.text.strip()
            # Extract price information
            price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', price_text)
            return price_match.group(0) if price_match else "N/A"
        return "N/A"
    
    def _extract_rating(self, elem, selector: str) -> str:
        rating_elem = elem.select_one(selector)
        if rating_elem:
            rating_text = rating_elem.text.strip()
            # Extract rating information
            rating_match = re.search(r'\d\.\d', rating_text)
            return rating_match.group(0) if rating_match else "N/A"
        return "N/A"