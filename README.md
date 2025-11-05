# Data Pipeline Platform

> **A general-purpose, modular platform for scraping, analyzing, and automating data pipelines from any source.**
>
> Build your own data collection modules in minutes. Includes OpenHPI and News Scraper modules as reference implementations.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

The Data Pipeline Platform is a **general-purpose, modular system** for scraping, processing, and analyzing data from any source. Built with extensibility in mind, it provides a pluggable architecture where new data sources and analysis modules can be easily added.

### 📦 Built-in Modules

The platform currently includes **two complete modules** that demonstrate its versatility:

1. **OpenHPI Module** - A fully-featured module for the OpenHPI learning platform
   - Public course scraping (no credentials)
   - Course analytics and statistics
   - AI-powered insights using Google Gemini
   - Automation tools (batch enrollment, helpdesk monitoring - requires credentials)

2. **News Scraper Module** - A demonstration module for news aggregation
   - Scrapes Hacker News headlines (public, no authentication)
   - AI-powered sentiment analysis on headlines
   - Demonstrates the simplicity of adding new modules

### Key Features

- **🔌 Modular Architecture** - Pluggable scraper and analyzer modules for any data source
- **📂 Source Management** - Define, configure, and manage multiple data sources through a unified interface
- **🔄 Generic Scraping** - Flexible scraping framework supporting public and authenticated sources
- **💾 Generic Data Storage** - Source, ScrapedData, and ProcessedData tables for any content type
- **🎨 Interactive Dashboard** - Beautiful Streamlit UI for managing sources and viewing data
- **🚀 REST API** - Comprehensive FastAPI backend with automatic documentation
- **📊 Multiple Example Modules** - OpenHPI and News Scraper modules included
- **🤖 AI Integration** - Google Gemini integration for intelligent analysis
- **⚡ Automation Support** - Extensible automation framework
- **🐳 Docker Ready** - Complete containerization for easy deployment
- **👨‍💻 Developer-Friendly** - Clear guide for adding new modules

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     User Interface Layer                        │
│                                                                  │
│  ┌──────────────────┐              ┌──────────────────────┐   │
│  │  Streamlit UI    │              │   CLI Interface      │   │
│  │  (Dashboard)     │              │   (Typer)            │   │
│  └────────┬─────────┘              └──────────┬───────────┘   │
│           │                                    │               │
└───────────┼────────────────────────────────────┼───────────────┘
            │                                    │
            ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                        API Layer                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │               FastAPI REST API                            │ │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐     │ │
│  │  │Course│  │Scrape│  │Analyt│  │Automa│  │  AI  │     │ │
│  │  │ API  │  │ API  │  │ API  │  │ API  │  │ API  │     │ │
│  │  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘     │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────┬───────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                    Service Layer                                 │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │  Scraping   │  │ Automation  │  │   AI Analysis       │   │
│  │  Service    │  │  Service    │  │   Service           │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │  Course     │  │   Quiz      │  │   Annual Stats      │   │
│  │  Parser     │  │  Analytics  │  │   Analytics         │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                    Data Layer                                    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              PostgreSQL / SQLite Database                 │ │
│  │                                                            │ │
│  │  ┌────────┐  ┌─────────┐  ┌──────┐  ┌────────────┐     │ │
│  │  │Courses │  │  Users  │  │ Quiz │  │ Analytics  │     │ │
│  │  │        │  │         │  │Results│  │   Data     │     │ │
│  │  └────────┘  └─────────┘  └──────┘  └────────────┘     │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

![System Architecture Diagram](docs/images/09-architecture-diagram.png)
*Visual representation of the platform's layered architecture*

## 🚀 Quick Start

### Using Docker (Recommended)

The fastest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/siddhant61/openhpi-automate.git
cd openhpi-automate

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start all services
docker-compose up -d

# Access the platform
# Dashboard: http://localhost:8501
# API Docs:  http://localhost:8000/docs
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📸 Platform Screenshots

Below are screenshots captured from a running local instance showcasing the platform's interfaces.

### Dashboard & UI

![Dashboard Home](docs/images/01-dashboard-home.png)
*Dashboard homepage with navigation sidebar and welcome screen*

![Analytics Page](docs/images/02-analytics-page.png)
*Interactive analytics page with Plotly charts showing course metrics*

![AI Insights](docs/images/03-ai-insights.png)
*AI-powered insights page with Google Gemini integration*

![Automation Tools](docs/images/04-automation-page.png)
*Automation interface for batch enrollment and helpdesk monitoring*

### API Documentation

![Swagger UI](docs/images/05-api-docs-swagger.png)
*FastAPI Swagger UI with interactive API documentation*

![ReDoc Interface](docs/images/06-api-docs-redoc.png)
*Alternative ReDoc documentation interface*

![API Endpoints](docs/images/11-api-endpoints.png)
*Complete API endpoint overview organized by modules*

![API Response](docs/images/12-api-response.png)
*Example JSON response from the courses API endpoint*

> **Note:** To regenerate screenshots automatically, use `python scripts/capture_web_screenshots.py` (requires Playwright and running services).

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Initialize database
python -m src.cli init

# Start API server
python -m src.cli serve

# In another terminal, start dashboard
streamlit run src/dashboard.py
```

## 📚 Features in Detail

### 1. Web Dashboard (Streamlit)

The interactive web dashboard provides:

- **📈 Course Metrics** - KPIs, enrollment trends, completion rates
- **📊 Annual Statistics** - Year-over-year reports with German/English breakdown
- **🎯 Quiz Performance** - Overall metrics, by-course, and by-type analysis
- **🤖 AI Insights** - Course summaries, feedback sentiment, key concepts
- **⚙️ Automation Tools** - Batch enrollment, helpdesk monitoring
- **📋 Data Management** - Import/export, bulk operations

**Access:** http://localhost:8501

### 2. REST API (FastAPI)

Comprehensive API with 19 endpoints across 5 modules:

#### Courses API
- `GET /api/courses/` - List all courses with filtering
- `GET /api/courses/{id}` - Get course details
- `GET /api/courses/{id}/stats` - Get course statistics

#### Scraping API
- `POST /api/scraping/courses` - Scrape course list
- `GET /api/scraping/jobs` - List scraping jobs
- `GET /api/scraping/jobs/{id}` - Get job details

#### Analysis API
- `GET /api/analysis/courses/metrics` - Course performance metrics
- `GET /api/analysis/annual` - Annual statistics
- `GET /api/analysis/quiz/performance` - Quiz analytics
- `POST /api/analysis/quiz/compare` - Compare quiz performance
- `GET /api/analysis/enrollments/trends` - Enrollment trends

#### Automation API
- `POST /api/automation/batch-enroll` - Batch user enrollment
- `POST /api/automation/check-helpdesk` - Check helpdesk tickets

#### AI API
- `POST /api/ai/summarize` - Generate course summary
- `POST /api/ai/analyze-feedback` - Analyze survey feedback
- `GET /api/ai/insights/{course_id}` - Get course insights

**Interactive Documentation:** http://localhost:8000/docs

### 3. CLI Commands

15 rich command-line tools for automation:

```bash
# Initialization
python -m src.cli init                    # Initialize database
python -m src.cli config                  # View configuration

# Server
python -m src.cli serve                   # Start API server
python -m src.cli serve --reload          # Development mode

# Scraping
python -m src.cli scrape courses          # Scrape course list
python -m src.cli scrape course-data      # Scrape course details

# Analytics
python -m src.cli analytics annual 2024   # Generate annual report
python -m src.cli analytics courses       # Course metrics
python -m src.cli analytics quiz          # Quiz performance

# Automation
python -m src.cli automate enroll         # Batch enrollment
python -m src.cli automate helpdesk       # Check helpdesk

# AI
python -m src.cli ai summarize            # Generate summaries
python -m src.cli ai feedback             # Analyze feedback
```

## 🔧 Configuration

All configuration is managed through environment variables in `.env`:

### Required Settings

```env
# OpenHPI Platform
OPENHPI_USERNAME=your-username
OPENHPI_PASSWORD=your-password

# Google AI (for analytics)
GOOGLE_API_KEY=your-api-key
```

### Optional Settings

```env
# Database (defaults to SQLite)
DATABASE_URL=postgresql://user:pass@localhost:5432/openhpi

# API Server
API_HOST=localhost
API_PORT=8000
API_WORKERS=4

# Notifications
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Paths
DATA_DIR=./data
REPORTS_DIR=./reports
EXPORTS_DIR=./exports
```

See [.env.example](.env.example) for all available options.

## 📊 Database Schema

The platform uses a unified database with 8 main tables:

| Table | Purpose |
|-------|---------|
| `courses` | Course metadata and information |
| `course_stats` | Historical statistics and KPIs |
| `users` | User accounts and profiles |
| `enrollments` | User-course enrollments with progress |
| `quiz_results` | Quiz performance data |
| `survey_responses` | Survey feedback and responses |
| `helpdesk_tickets` | Support ticket tracking |
| `scraping_jobs` | Job execution tracking |

### Database Migrations

```bash
# Check current version
alembic current

# Upgrade to latest
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"
```

## 🧪 Testing

The platform includes comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_scraping_service.py

# Run with verbose output
pytest -v
```

**Test Coverage:** 60% overall
- Core services: 92-100%
- Analysis modules: 79-96%
- API endpoints: 70-100%

## 🐳 Docker Deployment

### Services

The platform consists of 3 Docker services:

1. **API** (FastAPI) - Port 8000
2. **Dashboard** (Streamlit) - Port 8501
3. **Database** (PostgreSQL) - Port 5432

### Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose build && docker-compose up -d

# Run CLI commands
docker-compose exec api python -m src.cli --help

# Database backup
docker-compose exec db pg_dump -U openhpi openhpi_automation > backup.sql
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide.

## 📖 API Documentation

The API provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Usage

```python
import requests

# Get all courses
response = requests.get("http://localhost:8000/api/courses/")
courses = response.json()

# Get course metrics
response = requests.get("http://localhost:8000/api/analysis/courses/metrics?year=2024")
metrics = response.json()

# Generate AI summary
response = requests.post(
    "http://localhost:8000/api/ai/summarize",
    json={
        "title": "Python for Beginners",
        "description": "Learn Python programming from scratch..."
    }
)
summary = response.json()
```

```bash
# Using curl
curl http://localhost:8000/health

curl -X POST http://localhost:8000/api/scraping/courses

curl "http://localhost:8000/api/courses/?language=English&limit=10"
```

## 👨‍💻 Developer Guide: Adding a New Module

One of the platform's core strengths is its modularity. This guide shows you how to add your own scraper and analysis module in just a few steps.

### Module Architecture

Each module consists of two main components:

1. **Scraper** - Fetches raw data from a source and saves to `ScrapedData` table
2. **Analyzer** (optional) - Processes raw data and saves results to `ProcessedData` table

### Step 1: Create Module Structure

Create a new directory under `src/modules/`:

```bash
mkdir -p src/modules/your_module/
touch src/modules/your_module/__init__.py
touch src/modules/your_module/scraper.py
touch src/modules/your_module/analysis.py  # optional
```

### Step 2: Implement the Scraper

Create your scraper in `scraper.py`. Here's a minimal example based on the News Scraper:

```python
# src/modules/your_module/scraper.py
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from typing import Dict

from src.models.tables import Source, ScrapedData, ProcessedData, ScrapingJob
from src.core.utils import utcnow


def scrape_your_data(db: Session, source_id: int) -> Dict:
    """
    Main scraper function - this signature is required.
    
    Args:
        db: Database session
        source_id: ID of the source to scrape
        
    Returns:
        Dict with 'success' and other result data
    """
    # 1. Get the source
    source = db.query(Source).filter_by(id=source_id).first()
    if not source:
        raise ValueError(f"Source with id {source_id} not found")
    
    # 2. Create a scraping job
    job = ScrapingJob(
        job_type="your_module",
        status="running",
        started_at=utcnow()
    )
    db.add(job)
    db.commit()
    
    try:
        # 3. Scrape the data
        response = requests.get(source.url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract your data
        items = []
        for element in soup.find_all('div', class_='your-class'):
            items.append({
                'title': element.find('h2').text,
                'url': element.find('a')['href'],
                # ... other fields
            })
        
        # 4. Save to ScrapedData
        scraped = ScrapedData(
            source_id=source.id,
            url=source.url,
            raw_html=response.text,
            raw_json={'items': items},
            scraped_at=utcnow(),
            status_code=response.status_code
        )
        db.add(scraped)
        db.flush()
        
        # 5. Create ProcessedData records
        for item in items:
            processed = ProcessedData(
                scraped_data_id=scraped.id,
                title=item['title'],
                content_text=item.get('description', ''),
                data_metadata={'url': item['url']},
                processor_module='your_module',
                processed_at=utcnow()
            )
            db.add(processed)
        
        # 6. Update job
        job.status = "completed"
        job.completed_at = utcnow()
        job.records_processed = len(items)
        db.commit()
        
        return {
            'success': True,
            'items_count': len(items),
            'scraped_data_id': scraped.id
        }
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
        raise
```

### Step 3: Implement the Analyzer (Optional)

If you want to add analysis (like sentiment, classification, etc.):

```python
# src/modules/your_module/analysis.py
from sqlalchemy.orm import Session
from typing import Dict

from src.models.tables import ProcessedData, ScrapedData
from src.services.ai_service import AIService


def analyze_your_data(db: Session, scraped_data_id: int) -> Dict:
    """
    Analyze processed data - this signature is required.
    
    Args:
        db: Database session
        scraped_data_id: ID of the scraped data to analyze
        
    Returns:
        Dict with analysis results
    """
    # Get processed items
    items = db.query(ProcessedData).filter_by(
        scraped_data_id=scraped_data_id
    ).all()
    
    if not items:
        return {'success': True, 'analyzed_count': 0}
    
    # Use AI service for analysis (optional)
    ai_service = AIService()
    
    for item in items:
        if ai_service.enabled:
            # Perform AI analysis
            # Example: sentiment analysis, classification, etc.
            pass
        
        # Update the processed data
        item.sentiment_score = 0.5  # Your analysis result
        item.data_metadata = item.data_metadata or {}
        item.data_metadata['analyzed'] = True
    
    db.commit()
    
    return {
        'success': True,
        'analyzed_count': len(items)
    }
```

### Step 4: Register Your Module

Register your scraper and analyzer with the orchestrators:

```python
# src/services/scraping_orchestrator.py
def _register_default_scrapers(self):
    # ... existing code ...
    
    try:
        from src.modules.your_module.scraper import scrape_your_data
        self.register_scraper('your_module', scrape_your_data)
        logger.info("Registered Your Module scraper")
    except ImportError as e:
        logger.warning(f"Could not register Your Module scraper: {e}")
```

```python
# src/services/analysis_orchestrator.py
def _register_default_analyzers(self):
    # ... existing code ...
    
    try:
        from src.modules.your_module.analysis import analyze_your_data
        self.register_analyzer('your_module', analyze_your_data)
        logger.info("Registered Your Module analyzer")
    except ImportError as e:
        logger.warning(f"Could not register Your Module analyzer: {e}")
```

### Step 5: Create Tests

Always test your module:

```python
# tests/test_your_module.py
import pytest
from unittest.mock import Mock, patch

from src.modules.your_module.scraper import scrape_your_data

def test_your_scraper(test_db):
    # ... test implementation
    pass
```

### Step 6: Use Your Module

That's it! Your module is now integrated. Use it via:

**Dashboard:**
1. Go to "Source Manager" → "Add New Source"
2. Select "your_module" from the dropdown
3. Enter the URL and click "Add Source"
4. Click "Scrape Now" to run it

**API:**
```bash
# Create a source
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Data Source",
    "url": "https://example.com",
    "source_type": "your_type",
    "module_name": "your_module",
    "is_active": true
  }'

# Scrape it
curl -X POST http://localhost:8000/api/data/scrape/1
```

**CLI:**
```bash
python -m src.cli scrape-source --source-id 1
```

### Real-World Examples

The platform includes two complete examples:

1. **OpenHPI Module** (`src/modules/openhpi/`) - Complex module with multiple scrapers, private API integration, and rich analytics
2. **News Scraper Module** (`src/modules/news_scraper/`) - Simple module showing basic scraping and AI sentiment analysis

Study these for inspiration!

### Best Practices

- ✅ Use `requests` + `BeautifulSoup` for simple sites
- ✅ Save raw data to `ScrapedData` before processing
- ✅ Use the `processor_module` field to identify your module
- ✅ Handle errors gracefully and update job status
- ✅ Write tests for your scraper and analyzer
- ✅ Use the AI service for analysis when appropriate
- ⚠️ Only use Selenium if absolutely necessary (e.g., JavaScript-heavy sites)
- ⚠️ Be respectful: set appropriate user agents and rate limits

## 🤝 Contributing

Contributions are welcome! This project follows standard GitHub workflow:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and install
git clone https://github.com/siddhant61/openhpi-automate.git
cd openhpi-automate
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/
```

## 🔒 Security

- ✅ No hardcoded credentials
- ✅ Environment-based configuration
- ✅ Secure password storage
- ✅ API authentication ready
- ✅ HTTPS compatible
- ✅ Input validation
- ✅ SQL injection protection

**Important:** Never commit the `.env` file to version control!

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenHPI** for providing the platform
- **FastAPI** for the excellent web framework
- **Streamlit** for the interactive UI framework
- **Google Gemini** for AI capabilities

## 📧 Support

For issues, questions, or contributions:

- **GitHub Issues**: [Report a bug](https://github.com/siddhant61/openhpi-automate/issues)
- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- **Email**: Contact the maintainers

## 🗺️ Roadmap

**Completed:**
- ✅ Generic platform architecture
- ✅ Modular scraper system with orchestration
- ✅ Multiple example modules (OpenHPI, News Scraper)
- ✅ Generic data tables (Source, ScrapedData, ProcessedData)
- ✅ AI integration for analysis
- ✅ Comprehensive developer guide

**Planned:**
- [ ] More example modules (RSS feeds, social media, etc.)
- [ ] Advanced user analytics dashboard
- [ ] Real-time notifications system
- [ ] Enhanced AI features (summarization, classification)
- [ ] Plugin marketplace for community modules
- [ ] API v2 with GraphQL support

---

**Made with ❤️ by [Siddhant Gadamsetti](https://github.com/siddhant61)**
