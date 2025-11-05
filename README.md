# OpenHPI Automation Platform

> **A production-ready, full-stack automation and analytics platform for the OpenHPI course management system.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

The OpenHPI Automation Platform is a comprehensive solution that unifies course data scraping, analytics, AI-powered insights, and automated workflows into a single, production-ready application. Built with modern technologies and best practices, it provides both a web interface and a REST API for seamless integration.

### Key Features

- **🤖 AI-Powered Analysis** - Google Gemini integration for intelligent course summaries and feedback analysis
- **📊 Advanced Analytics** - Course metrics, quiz performance tracking, and enrollment trend analysis
- **⚡ Batch Automation** - Automated user enrollment, helpdesk monitoring, and notifications
- **🎨 Interactive Dashboard** - Beautiful Streamlit UI for data visualization and insights
- **🚀 REST API** - Comprehensive FastAPI backend with automatic documentation
- **💾 Unified Database** - Central PostgreSQL/SQLite database replacing CSV-based storage
- **🐳 Docker Ready** - Complete containerization for easy deployment
- **📝 CLI Tools** - Rich command-line interface for automation tasks

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
└──────────────────────────┬───────────────────────────────────┘
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

- [ ] Advanced user analytics
- [ ] Real-time notifications
- [ ] Multi-language support
- [ ] Enhanced AI features
- [ ] Mobile app
- [ ] API v2 with GraphQL

---

**Made with ❤️ by [Siddhant Gadamsetti](https://github.com/siddhant61)**
