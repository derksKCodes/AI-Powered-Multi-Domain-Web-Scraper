from typing import List, Dict, Any
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from pathlib import Path
import time
import pandas as pd

class BooksScraper(BaseScraper):
    def __init__(self):
        super().__init__("books")
    
    def scrape(self, max_pages: int = None) -> List[Dict[str, Any]]:
        """Scrape books data from multiple pages"""
        all_books = []
        
        pages_to_scrape = max_pages or self.config.get('pages', 5)
        
        for page in range(1, pages_to_scrape + 1):
            url = f"{self.config['base_url']}catalogue/page-{page}.html"
            response = self.make_request(url)
            
            if not response:
                continue
            
            soup = self.parse_html(response.text)
            books = self._parse_books_page(soup)
            all_books.extend(books)
            
            self.logger.info(f"Scraped page {page}: {len(books)} books")
            time.sleep(self.config.get('delay', 1.0))
        
        return all_books
    
    def _parse_books_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse a single page of books"""
        books = []
        selectors = self.config['selectors']
        book_elements = soup.select(selectors['book'])
        
        for book_elem in book_elements:
            try:
                book = {
                    'title': self._extract_text(book_elem, selectors['title']),
                    'price': self._extract_price(book_elem, selectors['price']),
                    'rating': self._extract_rating(book_elem, selectors['rating']),
                    'availability': self._extract_text(book_elem, selectors['availability']),
                    'url': self._extract_url(book_elem, selectors['title']),
                    'scraped_timestamp': pd.Timestamp.now()
                }
                books.append(book)
            except Exception as e:
                self.logger.error(f"Error parsing book: {e}")
                continue
        
        return books
    
    def _extract_text(self, elem, selector: str) -> str:
        selected = elem.select_one(selector)
        return selected.text.strip() if selected else "N/A"
    
    def _extract_price(self, elem, selector: str) -> float:
        price_text = self._extract_text(elem, selector)
        try:
            return float(re.sub(r'[^\d.]', '', price_text))
        except:
            return 0.0
    
    def _extract_rating(self, elem, selector: str) -> str:
        rating_elem = elem.select_one(selector)
        if rating_elem:
            rating_classes = rating_elem.get('class', [])
            return rating_classes[1] if len(rating_classes) > 1 else 'No rating'
        return 'No rating'
    
    def _extract_url(self, elem, selector: str) -> str:
        link_elem = elem.select_one(selector)
        if link_elem and link_elem.get('href'):
            relative_url = link_elem['href']
            if relative_url.startswith('http'):
                return relative_url
            return f"{self.config['base_url']}{relative_url}"
        return "N/A"