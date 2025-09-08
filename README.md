# AI-Powered Multi-Domain Web Scraper

A modular, extensible system for scraping and analyzing data from multiple domains (Books, Jobs, Real Estate, E-commerce, Education). Data is stored in structured formats (CSV, JSON, Excel, Postgres, MySQL), and Generative AI is integrated for automated insights and report generation.

---

## 🎯 About The Project

This project enables rapid data collection and AI-powered analysis across diverse domains. Its modular design allows you to add new scrapers with minimal effort—just one new file per domain.

---

## ✨ Features

- **Multi-domain scraping:** Books, Jobs, Real Estate, E-commerce, Education
- **Structured data storage:** CSV, JSON, Excel, Postgres, MySQL
- **AI-powered analysis:** Automated insights and markdown reports via OpenAI GPT
- **CLI interface:** Simple commands for scraping, analysis, and full pipeline runs
- **Extensible architecture:** Add new scrapers and analysis modules easily
- **Config-driven:** Scraper parameters are set via JSON files—no code changes needed

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **Requests, BeautifulSoup, pandas, SQLAlchemy**
- **OpenAI GPT API**
- **Postgres, MySQL, SQLite (optional)**
- **CLI via argparse**

---

## 📁 Project Structure

```
multi_scraper_ai/
│── data/                       # scraped data storage
│   ├── books/
│   │   └── books_url.json
│   ├── jobs/
│   │   └── jobs_url.json
│   ├── real_estate/
│   │   └── real_estate_url.json
│   ├── ecommerce/
│   │   └── ecommerce_url.json
│   └── education/
│       └── education_url.json
│
│── scrapers/                   
│   ├── __init__.py
│   ├── books_scraper.py        
│   ├── jobs_scraper.py         
│   ├── real_estate_scraper.py  
│   ├── ecommerce_scraper.py    
│   ├── education_scraper.py    
│   └── base_scraper.py         
│
│── analysis/                   
│   ├── __init__.py
│   ├── books_analysis.py
│   ├── jobs_analysis.py
│   ├── real_estate_analysis.py
│   ├── ecommerce_analysis.py
│   ├── education_analysis.py
│   └── base_analysis.py
│
│── outputs/ 
│   ├── report/               
│   │   ├── books_report.md
│   │   ├── jobs_report.md
│   │   ├── real_estate_report.md
│   │   ├── ecommerce_report.md
│   │   └── education_report.md
│   └── scrapped_data/
│       ├── books/
│       ├── jobs/
│       ├── real_estate/
│       ├── ecommerce/
│       └── education/
│
│── utils/                      
│   ├── __init__.py
│   ├── db.py                   
│   ├── excel_utils.py
│   ├── text_cleaner.py
│   └── config.py
│
│── run.py                      
│── requirements.txt
│── .env
│── README.md
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up environment variables

```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
echo "DB_HOST=localhost" >> .env
echo "DB_NAME=scraper_db" >> .env
```

### 3. Create necessary directories

```bash
mkdir -p data/books data/jobs data/real_estate data/ecommerce data/education
mkdir -p outputs/scrapped_data/books outputs/scrapped_data/jobs outputs/scrapped_data/real_estate outputs/scrapped_data/ecommerce outputs/scrapped_data/education
mkdir -p outputs/report
```

---

## 📱 Usage

### Scrape data

```bash
python run.py scrape books --pages 3
python run.py scrape jobs --pages 2
python run.py scrape ecommerce --pages 2
```

### Analyze data with AI

```bash
python run.py analyze books
python run.py analyze jobs
```

### Run complete pipeline

```bash
python run.py run-all jobs --pages 2
```

---

## 🤖 AI Integration

- Each analysis module uses OpenAI GPT to generate insights and markdown reports.
- Reports are saved in `outputs/report/` for each domain.

---

## 🌐 Deployment

- Can be run locally or deployed on a server.
- Supports database storage (Postgres/MySQL) for scalable deployments.

---

## 🎨 Customization & Extending

**To add a new domain:**
1. Create a new scraper: `scrapers/{site}_scraper.py`
2. Add an analysis module: `analysis/{site}_analysis.py`
3. Register your scraper in `run.py`
4. Add config/data files in `data/{site}/`

---

## 📸 Screenshots

*(Add screenshots of CLI usage, sample reports, and data outputs here)*

---

## 🤝 Contributing

Pull requests and suggestions are welcome! Please open issues for bugs or feature requests.

---

## 📄 License

MIT License

---

## 📞 Contact

- Project Author: Derrick@cyphertechs
- Portfolio: http://derrickportfolioweb.vercel.app/
- GitHub: https://github.com/derksKCodes

---

## Example Use Cases

- **Books:** “Which genres are cheapest on BooksToScrape right now?”
- **Jobs:** “Summarize the top 5 tech skills from RemoteOK this week.”
- **Real Estate:** “Generate an AI report on average 3-bedroom house prices in London vs. Manchester.”
- **E-commerce:** “Compare prices of Apple products across Amazon sellers.”
- **Education:** “List the top 5 AI-related Coursera courses and summarize reviews.”

---

## How It Works

1. **Choose Website:**  
   Run the project with an argument:
   ```bash
   python run.py scrape books
   python run.py site jobs
   python run.py site ecommerce
   ```

2. **Scraper Extracts Data:**  
   - Books → Title, Author, Price, Rating
   - Jobs → Title, Company, Skills, Salary, Location
   - Real Estate → Location, Price, Bedrooms, Agent Contact
   - E-commerce → Product, Price, Rating, Availability
   - Education → Course Name, Instructor, Rating, Duration

3. **AI Analysis:**  
   - Books → Summarize most popular genres
   - Jobs → Identify top 10 skills in demand
   - Real Estate → Compare avg price per location
   - E-commerce → Generate competitor analysis
   - Education → Summarize trending courses

4. **Save Output:**  
   - Data → `data/` (CSV/JSON)
   - AI Insights → `outputs/report/` (Markdown reports)

---

## Extending

To add a new website:
- Create a new scraper in `scrapers/`
- Add an AI analysis script in `analysis/