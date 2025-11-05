# OpenHPI Automation Suite

> **🚧 Active Refactoring**: This project is being transformed from a collection of scripts into a unified, production-ready automation platform.

A comprehensive automation and analytics platform for the OpenHPI course management system. This suite provides unified tools for course data scraping, user management, analytics, and automated workflows.

## 🎯 Project Status

**Phase 1: Project Unification & Configuration** ✅ **COMPLETE**

The foundational architecture has been established:
- ✅ Unified project structure with `src/` layout
- ✅ Centralized configuration management (`.env` + `pydantic-settings`)
- ✅ Database layer with SQLAlchemy models
- ✅ FastAPI backend foundation
- ✅ CLI interface with Typer
- ✅ All hardcoded credentials removed from codebase

**Next Phases**: Data ingestion refactoring, analysis layer, automation services, UI development, and AI integration.

## 🏗️ Architecture

```
openhpi-automate/
├── src/                      # Main application code
│   ├── api/                  # FastAPI routes and endpoints
│   ├── services/             # Business logic (scraping, automation, AI)
│   ├── core/                 # Configuration and utilities
│   ├── models/               # Database models
│   ├── analysis/             # Analytics and statistics
│   ├── main.py              # FastAPI application
│   └── cli.py               # Command-line interface
├── tests/                    # Test suite
├── data/                     # Data storage (gitignored)
├── reports/                  # Generated reports (gitignored)
├── .env                      # Environment configuration (gitignored)
├── .env.example             # Template for configuration
├── pyproject.toml           # Project metadata and dependencies
└── requirements.txt         # Python dependencies
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/siddhant61/openhpi-automate.git
cd openhpi-automate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env with your credentials
```

### 2. Configuration

Edit `.env` file with your credentials:

```env
# OpenHPI Platform
OPENHPI_USERNAME="your-username"
OPENHPI_PASSWORD="your-password"

# Google AI (for analytics)
GOOGLE_API_KEY="your-api-key"

# Email notifications
SMTP_USERNAME="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"

# Telegram notifications
TELEGRAM_BOT_TOKEN="your-bot-token"
TELEGRAM_CHAT_ID="your-chat-id"
```

### 3. Initialize

```bash
# Initialize database and directories
python -m src.cli init

# Verify configuration
python -m src.cli config
```

### 4. Run

```bash
# Start API server
python -m src.cli serve

# Or run specific tasks
python -m src.cli scrape courses
python -m src.cli analytics annual 2024
```

## 📚 Features

### Current Features (Phase 1)
- ✅ **Centralized Configuration**: All settings managed via `.env` file
- ✅ **Database Layer**: SQLAlchemy models for courses, users, enrollments, analytics
- ✅ **REST API**: FastAPI backend with automatic documentation
- ✅ **CLI Interface**: Rich command-line interface for all operations
- ✅ **Security**: No hardcoded credentials, proper secret management

### Upcoming Features
- 🔄 **Data Scraping**: Requests-based scraping (replacing Selenium)
- 🔄 **Analytics Engine**: Course statistics, annual reports, quiz analysis
- 🔄 **Automation**: Batch enrollment, page updates, notifications
- 🔄 **AI Analysis**: Google Gemini integration for course insights
- 🔄 **Dashboard UI**: Interactive Streamlit/Dash interface
- 🔄 **API Endpoints**: Full CRUD operations for all entities

## 🛠️ Development

### Database

```bash
# Initialize/reset database
python -m src.cli init

# View database schema
sqlite3 openhpi_automation.db ".schema"
```

### API Server

```bash
# Development mode (with auto-reload)
python -m src.cli serve --reload

# Access API documentation
open http://localhost:8000/docs
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## 📦 Database Schema

The unified database replaces all CSV-based data storage:

- **courses**: Course metadata and information
- **course_stats**: Historical statistics and KPIs
- **users**: User accounts and profiles
- **enrollments**: User-course enrollments with progress
- **quiz_results**: Quiz performance data
- **survey_responses**: Survey feedback
- **helpdesk_tickets**: Support ticket tracking
- **scraping_jobs**: Job execution tracking

## 🔧 Configuration Options

See `.env.example` for all available configuration options:

```env
# Platform credentials
OPENHPI_USERNAME, OPENHPI_PASSWORD
HELPDESK_USERNAME, HELPDESK_PASSWORD

# Integrations
GOOGLE_API_KEY
TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
SMTP_USERNAME, SMTP_PASSWORD

# Database
DATABASE_URL="sqlite:///./openhpi_automation.db"

# Paths
DATA_DIR, REPORTS_DIR, EXPORTS_DIR

# API Server
API_HOST, API_PORT, API_WORKERS
```

## 📖 API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Current endpoints:
- `GET /` - API information
- `GET /health` - Health check

## 🧪 Legacy Scripts

The root directory contains legacy scripts from the original implementation. These are being incrementally refactored into the new unified architecture:

**⚠️ Deprecated - Do Not Use**:
- `batch_enroll.py`, `course_scraper.py`, `data_scraper.py` - Use new services instead
- `course_analytics.py`, `quiz_analysis.py` - Use API analytics endpoints
- `helpdesk_notifier.py` - Use automation service

These files will be removed once all functionality is migrated to the new architecture.

## 🤝 Contributing

This is an active refactoring project. The goal is to create a production-ready, maintainable automation platform. See the problem statement in the PR for the complete migration plan.

## 📝 License

MIT License - See LICENSE file for details.

## 🔒 Security

- Never commit the `.env` file
- All credentials must be loaded from environment variables
- Use `.env.example` as a template for required configuration
- API keys and tokens should be rotated regularly 