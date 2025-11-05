# Screenshot Guide for OpenHPI Automation Platform

This document provides a comprehensive list of screenshots needed to complete the documentation. Each screenshot should be saved in the `docs/images/` directory with the exact filename specified.

## 📸 Shot List

### Dashboard Screenshots (Streamlit UI)

#### 01-dashboard-home.png
**Description:** Main dashboard homepage
**URL:** http://localhost:8501
**Instructions:**
- Navigate to the Streamlit dashboard homepage
- Ensure the sidebar is visible showing all navigation options
- Capture the main welcome/overview page with key metrics or navigation cards
- Should show the clean, professional interface
**Recommended Size:** 1920x1080 or 1440x900

#### 02-analytics-page.png
**Description:** Analytics page with Plotly charts
**URL:** http://localhost:8501 (navigate to Analytics page)
**Instructions:**
- Navigate to the "Analytics" or "Course Metrics" section
- Show interactive Plotly charts (bar charts, line graphs, etc.)
- Include visible course performance data and metrics
- Ensure charts are fully rendered and visually appealing
**Recommended Size:** 1920x1080 or 1440x900

#### 03-ai-insights.png
**Description:** AI-powered insights page
**URL:** http://localhost:8501 (navigate to AI Insights page)
**Instructions:**
- Navigate to the "AI Insights" or "AI Analysis" section
- Show an example of AI-generated course summary or feedback analysis
- Include Google Gemini integration results
- Highlight the AI-generated text and key insights
**Recommended Size:** 1920x1080 or 1440x900

#### 04-automation-page.png
**Description:** Automation tools interface
**URL:** http://localhost:8501 (navigate to Automation page)
**Instructions:**
- Navigate to the "Automation" section
- Show the batch enrollment form or helpdesk monitoring interface
- Include form fields and action buttons
- Demonstrate the user-friendly automation interface
**Recommended Size:** 1920x1080 or 1440x900

---

### API Documentation Screenshots (FastAPI)

#### 05-api-docs-swagger.png
**Description:** FastAPI Swagger UI documentation
**URL:** http://localhost:8000/docs
**Instructions:**
- Open the Swagger UI at /docs endpoint
- Expand a few endpoint sections to show details (e.g., Courses API, Analysis API)
- Show the interactive "Try it out" functionality
- Capture the complete list of endpoints organized by tags
**Recommended Size:** 1920x1080 or 1440x900

#### 06-api-docs-redoc.png
**Description:** FastAPI ReDoc documentation
**URL:** http://localhost:8000/redoc
**Instructions:**
- Open the ReDoc interface at /redoc endpoint
- Show the alternative documentation style
- Capture the navigation sidebar and endpoint details
- Highlight the clean, professional documentation layout
**Recommended Size:** 1920x1080 or 1440x900

#### 11-api-endpoints.png
**Description:** Complete endpoint list overview
**URL:** http://localhost:8000/docs
**Instructions:**
- Show the collapsed view of all API endpoints
- Ensure all 5 modules are visible (Courses, Scraping, Analysis, Automation, AI)
- Highlight the organized structure with color-coded tags
- Capture the OpenAPI schema information at the top
**Recommended Size:** 1920x1080 or 1440x900

#### 12-api-response.png
**Description:** Example API response in JSON format
**URL:** http://localhost:8000/docs (execute a GET request)
**Instructions:**
- Execute a sample GET request (e.g., GET /api/courses/)
- Show the JSON response with course data
- Include the response status code (200)
- Highlight the structured JSON format
- Can use browser DevTools Network tab or Swagger UI response section
**Recommended Size:** 1920x1080 or 1440x900

---

### CLI Screenshots (Terminal)

#### 07-cli-interface.png
**Description:** CLI help menu or command overview
**Command:** `python -m src.cli --help`
**Instructions:**
- Run the CLI help command to show all available commands
- Capture the rich, colorful terminal output (Typer interface)
- Show the organized command groups (init, serve, scrape, analytics, automate, ai)
- Use a terminal with good color support
**Recommended Size:** 1200x800 or terminal window size

#### 08-cli-output.png
**Description:** Example CLI output from an analytics command
**Command:** `python -m src.cli analytics courses` or similar
**Instructions:**
- Execute an analytics or automation command
- Show the formatted output with tables, progress bars, or results
- Capture the colorful, informative CLI feedback
- Include command execution and results
**Recommended Size:** 1200x800 or terminal window size

---

### Architecture & System Screenshots

#### 09-architecture-diagram.png
**Description:** Visual architecture diagram
**Instructions:**
- Create a visual diagram of the system architecture
- Can use tools like draw.io, Lucidchart, or Excalidraw
- Show the layered architecture: UI Layer → API Layer → Service Layer → Data Layer
- Include technology stack labels (Streamlit, FastAPI, PostgreSQL, etc.)
- Use the ASCII diagram in README.md as reference
**Recommended Size:** 1920x1080 or 1600x900

---

### Docker & Deployment Screenshots

#### 10-docker-containers.png
**Description:** Docker containers running
**Command:** `docker-compose ps` or Docker Desktop
**Instructions:**
- Show all three containers running (api, dashboard, db)
- Use either `docker ps` output or Docker Desktop UI
- Include container names, status, and ports
- Highlight the healthy status of all services
**Recommended Size:** 1440x900 or terminal window size

---

### Database Screenshots

#### 13-database-schema.png
**Description:** Database entity-relationship diagram
**Instructions:**
- Create an ERD showing the 8 main tables and their relationships
- Include: courses, course_stats, users, enrollments, quiz_results, survey_responses, helpdesk_tickets, scraping_jobs
- Show primary keys, foreign keys, and main relationships
- Can use tools like dbdiagram.io, pgModeler, or DBeaver's ERD feature
- Use a clean, professional database visualization style
**Recommended Size:** 1920x1080 or 1600x900

---

## 📝 General Guidelines

### Image Quality
- Use high-resolution screenshots (at least 1440x900 for desktop, 1200x800 for terminal)
- Ensure text is crisp and readable
- Avoid compression artifacts (use PNG format)

### Content
- Remove any sensitive information (passwords, API keys, personal data)
- Use sample/demo data where applicable
- Ensure UI is in a clean, complete state (no error messages unless intentional)

### Style
- Use a professional theme/color scheme
- Ensure good contrast and readability
- Capture complete UI elements (no cut-off buttons or text)

### File Format
- Save all images as PNG (for better quality with text/UI elements)
- Use the exact filenames specified above
- Place all files in `docs/images/` directory

### Browser/Terminal Settings
- Use a modern browser (Chrome, Firefox, Edge)
- Set browser zoom to 100%
- Use a terminal with good color support (e.g., Windows Terminal, iTerm2)
- Consider using a light theme for better readability in documentation

---

## ✅ Checklist

After capturing all screenshots, verify:

- [ ] All 13 screenshots are captured
- [ ] All files are saved in `docs/images/` directory
- [ ] All filenames match exactly (case-sensitive)
- [ ] All images are PNG format
- [ ] No sensitive information is visible
- [ ] Images are high-quality and readable
- [ ] README.md references match the captured screenshots

---

## 🚀 Quick Capture Workflow

1. **Start all services:**
   ```bash
   docker-compose up -d
   # or
   python -m src.cli serve  # in one terminal
   streamlit run src/dashboard.py  # in another terminal
   ```

2. **Open browser tabs:**
   - http://localhost:8501 (Dashboard)
   - http://localhost:8000/docs (API)
   - http://localhost:8000/redoc (API)

3. **Navigate and capture:**
   - Dashboard: Home → Analytics → AI Insights → Automation
   - API: Swagger → ReDoc → Execute sample requests
   - CLI: Run help commands and sample operations
   - Docker: Check container status

4. **Save all images** to `docs/images/` with correct names

5. **Verify in README.md** - all image links should work

---

**Note:** This guide is for the repository maintainer to capture and add screenshots. Once completed, this file can remain as reference or be removed from the repository.
