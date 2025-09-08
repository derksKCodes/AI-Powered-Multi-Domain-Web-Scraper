# scrapers/education_scraper.py
from typing import List, Dict, Any, Optional
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
from urllib.parse import urljoin
import concurrent.futures

class EducationScraper(BaseScraper):
    def __init__(self):
        super().__init__("education")

    def scrape(self, max_pages: int = None, search_term: str = "data science") -> List[Dict[str, Any]]:
        """Scrape education data from multiple pages (search results + instructor from detail page)."""
        all_courses: List[Dict[str, Any]] = []
        pages_to_scrape = max_pages or self.config.get("pages", 1)
        max_workers = self.config.get("max_workers", 5)  # for parallel instructor fetching

        for page in range(1, pages_to_scrape + 1):
            # build search URL safely (use quote_plus if needed)
            url = f"{self.config['base_url'].rstrip('/')}/search?query={search_term}&page={page}"
            response = self.make_request(url)
            if not response:
                continue

            soup = self.parse_html(response.text)
            courses_on_page = self._parse_courses_page(soup)
            self.logger.info(f"Found {len(courses_on_page)} raw course candidates on page {page}")

            # deduplicate by url
            all_courses: List[Dict[str, Any]] = []
            seen = set()   # track across ALL pages

            for page in range(1, pages_to_scrape + 1):
                url = f"{self.config['base_url'].rstrip('/')}/search?query={search_term}&page={page}"
                response = self.make_request(url)
                if not response:
                    continue

                soup = self.parse_html(response.text)
                courses_on_page = self._parse_courses_page(soup)
                self.logger.info(f"Found {len(courses_on_page)} raw course candidates on page {page}")

                # deduplicate against all previously seen
                filtered = []
                for c in courses_on_page:
                    u = c.get("url")
                    if not u or u in seen:
                        continue
                    seen.add(u)
                    filtered.append(c)


            # fetch instructors in parallel (safely)
            if filtered:
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
                    futures = {ex.submit(self._fetch_instructor, c["url"], self.config["selectors"].get("instructor")): c for c in filtered}
                    for f in concurrent.futures.as_completed(futures):
                        course = futures[f]
                        try:
                            instr = f.result()
                        except Exception as e:
                            self.logger.exception(f"Failed to fetch instructor for {course.get('url')}: {e}")
                            instr = "N/A"
                        course["instructor"] = instr
                        # stamp time (or keep earlier)
                        course["scraped_timestamp"] = pd.Timestamp.now()

            all_courses.extend(filtered)
            self.logger.info(f"Scraped page {page}: {len(filtered)} courses (after dedupe)")
            time.sleep(self.config.get("delay", 1.0))

        return all_courses

    def _parse_courses_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse search result page and return list of course dicts (instructor left for later)."""
        courses: List[Dict[str, Any]] = []
        sel = self.config.get("selectors", {})
        # sensible defaults in case config is missing keys:
        card_selector = sel.get("course_card", "li.ais-InfiniteHits-item, div.cds-ProductCard, div.cds-CommonCard")
        link_selector = sel.get("link", "a[data-click-key*='search.search.click.search_card']")
        title_selector = sel.get("title", "h3.cds-CommonCard-title, h2, h3")
        rating_selector = sel.get("rating", "span.css-6ecy9b")
        reviews_selector = sel.get("reviews", "div.css-vac8rf")
        skills_selector = sel.get("skills", "p.css-vac8rf")
        duration_selector = sel.get("duration", "div.cds-CommonCard-metadata p.css-vac8rf")

        cards = soup.select(card_selector)
        self.logger.debug(f"_parse_courses_page: found {len(cards)} cards with selector '{card_selector}'")

        for card in cards:
            try:
                # Find the link element inside the card (this filters out nav/footer links)
                link_elem = card.select_one(link_selector)
                if not link_elem:
                    # There are many non-course elements — skip
                    continue

                href = link_elem.get("href", "").strip()
                if not href:
                    continue

                course_url = urljoin(self.config["base_url"], href)

                # Title: prefer the title selector, fallback to the link text
                title = self._safe_text(card, title_selector)
                if not title:
                    title = link_elem.get_text(strip=True) or "N/A"

                # Rating
                rating = self._extract_rating(card, rating_selector)

                # Reviews: try to find the reviews-looking element
                reviews = self._extract_reviews(card, reviews_selector)

                # Skills
                skills = self._extract_skills(card, skills_selector)

                # Duration
                duration = self._safe_text(card, duration_selector)

                course = {
                    "course": title,
                    "rating": rating,
                    "reviews": reviews,
                    "skills": skills,
                    "duration": duration,
                    "url": course_url,
                    # instructor will be populated later via detail-page fetch
                    "instructor": "N/A",
                    "scraped_timestamp": pd.Timestamp.now()
                }
                courses.append(course)

            except Exception as e:
                self.logger.exception(f"Error parsing course card: {e}")
                continue

        return courses

    def _safe_text(self, elem, selector: str) -> str:
        if not elem or not selector:
            return "N/A"
        sel = elem.select_one(selector)
        if not sel:
            return "N/A"
        return sel.get_text(strip=True)

    def _extract_rating(self, elem, selector: str) -> str:
        if not selector:
            return "N/A"
        sel = elem.select_one(selector)
        if not sel:
            return "N/A"
        txt = sel.get_text(strip=True)
        m = re.search(r"\d+\.\d+", txt)
        return m.group(0) if m else txt or "N/A"

    def _extract_reviews(self, elem, selector: str) -> str:
        # Prefer explicit reviews text (e.g. "42K reviews")
        sel = elem.select_one(selector) if selector else None
        if sel:
            txt = sel.get_text(strip=True)
            # return only the reviews-looking string
            # e.g. "42K reviews" or "123 reviews"
            if "review" in txt.lower():
                return txt
            # sometimes reviews are embedded in other text; try to extract digits+K
            m = re.search(r"[\d,]+K?\s*reviews?", txt, re.IGNORECASE)
            if m:
                return m.group(0)
        return "N/A"

    def _extract_skills(self, elem, selector: str) -> str:
        if not selector:
            return "N/A"
        sel = elem.select_one(selector)
        if not sel:
            return "N/A"
        txt = sel.get_text(separator=", ", strip=True)
        # remove the leading label if present
        txt = re.sub(r"(?i)skills you'll gain[:\s-]*", "", txt)
        return txt or "N/A"

    def _fetch_instructor(self, course_url: str, selector: Optional[str]) -> str:
        """Fetch instructor(s) from course detail page. Returns 'N/A' on failure."""
        if not course_url:
            return "N/A"
        try:
            response = self.make_request(course_url)
            if not response:
                return "N/A"
            soup = self.parse_html(response.text)
            if not selector:
                selector = "p.css-4s48ix span"
            # sometimes instructors are in multiple elements
            elems = soup.select(selector)
            if not elems:
                # fallback: try other likely patterns
                alt = soup.select("a[href*='/instructor/'] span") or soup.select("span[class*='instructor']")
                elems = alt
            names = [e.get_text(strip=True) for e in elems if e.get_text(strip=True)]
            # dedupe and join
            names = list(dict.fromkeys(names))
            return ", ".join(names) if names else "N/A"
        except Exception as e:
            self.logger.exception(f"_fetch_instructor error for {course_url}: {e}")
            return "N/A"
