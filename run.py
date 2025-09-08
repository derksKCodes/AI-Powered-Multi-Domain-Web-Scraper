#!/usr/bin/env python3
import typer
from typing import Optional
from pathlib import Path
import importlib
import pandas as pd
from loguru import logger
import sys
import chardet
# Configure logging
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

app = typer.Typer(help="AI-Powered Multi-Domain Web Scraper")

# Available domains
DOMAINS = {
    'books': {
        'scraper': 'books_scraper.BooksScraper',
        'analysis': 'books_analysis.BooksAnalysis'
    },
    'jobs': {
        'scraper': 'jobs_scraper.JobsScraper',
        'analysis': 'jobs_analysis.JobsAnalysis'
    },
    'real_estate': {
        'scraper': 'real_estate_scraper.RealEstateScraper',
        'analysis': 'real_estate_analysis.RealEstateAnalysis'
    },
    'ecommerce': {
        'scraper': 'ecommerce_scraper.EcommerceScraper',
        'analysis': 'ecommerce_analysis.EcommerceAnalysis'
    },
    'education': {
        'scraper': 'education_scraper.EducationScraper',
        'analysis': 'education_analysis.EducationAnalysis'
    }
}

def load_class(module_path: str, module_type: str):
    """Dynamically load a class from module path"""
    module_name, class_name = module_path.rsplit('.', 1)
    if module_type == 'scraper':
        module = importlib.import_module(f"scrapers.{module_name}")
    else:
        module = importlib.import_module(f"analysis.{module_name}")
    return getattr(module, class_name)

@app.command()
def scrape(
    site: str = typer.Argument(..., help="Domain to scrape (books, jobs, real_estate, ecommerce, education)"),
    pages: int = typer.Option(None, help="Number of pages to scrape (overrides config)"),
    output: str = typer.Option("scraped_data", help="Output filename"),
    save_db: bool = typer.Option(False, help="Save to database")
):
    """Run scraper for a specific domain"""
    if site not in DOMAINS:
        logger.error(f"Domain {site} not supported. Available: {list(DOMAINS.keys())}")
        return
    
    try:
        # Load and run scraper
        scraper_class = load_class(DOMAINS[site]['scraper'], 'scraper')
        scraper = scraper_class()
        
        logger.info(f"Starting {site} scraper...")
        
        # Handle special parameters for specific scrapers
        if site == 'ecommerce':
            data = scraper.scrape(max_pages=pages, search_term="laptop")
        elif site == 'education':
            data = scraper.scrape(max_pages=pages, search_term="data science")
        else:
            data = scraper.scrape(max_pages=pages)
        
        if data:
            # Save to files
            scraper.save_data(data, output)
            
            # Optional: Save to database
            if save_db:
                from utils.db import DatabaseManager
                db_manager = DatabaseManager()
                db_manager.save_data(site, data, f"{site}_scraper")
            
            logger.success(f"Successfully scraped {len(data)} items from {site}")
        else:
            logger.warning(f"No data scraped from {site}")
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        


def read_file_with_fallback(file_path: Path):
    """Read file with encoding detection & fallback for CSV/JSON/Excel"""
    try:
        if file_path.suffix == '.csv':
            try:
                return pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                # Detect encoding dynamically
                with open(file_path, "rb") as f:
                    raw = f.read()
                enc = chardet.detect(raw)["encoding"] or "utf-8"
                return pd.read_csv(file_path, encoding=enc)

        elif file_path.suffix == '.json':
            return pd.read_json(file_path)

        elif file_path.suffix in ['.xls', '.xlsx']:
            return pd.read_excel(file_path)

        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
    except Exception as e:
        logger.error(f"Failed reading {file_path}: {e}")
        raise
    
@app.command()
def analyze(
    site: str = typer.Argument(..., help="Domain to analyze"),
    input_file: Optional[str] = typer.Option(None, help="Input data file"),
    generate_report: bool = typer.Option(True, help="Generate AI report")
):
    """Run analysis for a specific domain"""
    if site not in DOMAINS:
        logger.error(f"Domain {site} not supported. Available: {list(DOMAINS.keys())}")
        return
    
    try:
        # Import safe reading functions
        from utils.file_utils import safe_read_csv, safe_read_json, safe_read_excel
        
        # Load data
        if input_file:
            data_path = Path(f"outputs/scrapped_data/{site}/{input_file}")
            if not data_path.exists():
                logger.error(f"File not found: {data_path}")
                return
                
            if data_path.suffix == '.csv':
                data = safe_read_csv(data_path)
            elif data_path.suffix == '.json':
                data = safe_read_json(data_path)
            elif data_path.suffix in ['.xlsx', '.xls']:
                data = safe_read_excel(data_path)
            else:
                logger.error(f"Unsupported file format: {data_path.suffix}")
                return
        else:
            # Load latest data
            data_dir = Path(f"outputs/scrapped_data/{site}")
            if not data_dir.exists():
                logger.error(f"Data directory not found: {data_dir}")
                return
                
            files = list(data_dir.glob("*.csv")) + list(data_dir.glob("*.json")) + list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*.xls"))
            if not files:
                logger.error(f"No data files found for {site}")
                return
                
            # Get the latest file based on modification time
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            logger.info(f"Loading latest file: {latest_file}")
            
            if latest_file.suffix == '.csv':
                data = safe_read_csv(latest_file)
            elif latest_file.suffix == '.json':
                data = safe_read_json(latest_file)
            elif latest_file.suffix in ['.xlsx', '.xls']:
                data = safe_read_excel(latest_file)
            else:
                logger.error(f"Unsupported file format: {latest_file.suffix}")
                return
        
        # Check if data is empty
        if data.empty:
            logger.error(f"No data found in the file")
            return
            
        logger.info(f"Loaded {len(data)} records for analysis")
        
        # Load and run analysis
        analysis_class = load_class(DOMAINS[site]['analysis'], 'analysis')
        analyzer = analysis_class()
        
        logger.info(f"Analyzing {site} data...")
        insights = analyzer.analyze(data)
        
        if generate_report and 'ai_analysis' in insights:
            analyzer.save_report(insights['ai_analysis'], site, "market_analysis")
            logger.success(f"AI report generated for {site}")
        
        # Print basic insights
        item_count = insights.get('total_books', 
                                 insights.get('total_jobs', 
                                             insights.get('total_properties', 
                                                         insights.get('total_products', 
                                                                     insights.get('total_courses', 0)))))
        logger.info(f"Analysis completed. {item_count} items analyzed")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

@app.command()
def run_all(
    site: str = typer.Argument(..., help="Domain to process"),
    pages: int = typer.Option(None, help="Number of pages to scrape"),
    analyze_data: bool = typer.Option(True, help="Run analysis after scraping")
):
    """Run both scraping and analysis for a domain"""
    scrape(site=site, pages=pages)
    if analyze_data:
        analyze(site=site)

if __name__ == "__main__":
    app()