from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
SCRAPERS_DIR = BASE_DIR / "scrapers"
ANALYSIS_DIR = BASE_DIR / "analysis"

# Database configuration
DB_CONFIG = {
    'dialect': 'postgresql',
    'driver': 'psycopg2',
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'scraper_db'),
    'username': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')