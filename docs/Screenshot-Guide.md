# Screenshot Guide - OpenHPI Automation Platform

## Quick Start

### 1. Start Services
```bash
# Option A: Docker Compose
docker-compose up -d

# Option B: Manual
python -m src.cli serve &              # Terminal 1: FastAPI
streamlit run src/dashboard.py &       # Terminal 2: Streamlit
```

### 2. Install Playwright (First Time Only)
```bash
pip install -U playwright
python -m playwright install --with-deps chromium
```

### 3. Capture Web Screenshots (Automated)
```bash
python scripts/capture_web_screenshots.py
```

This captures:
- ✅ 01-dashboard-home.png
- ✅ 02-analytics-page.png
- ✅ 03-ai-insights.png
- ✅ 04-automation-page.png
- ✅ 05-api-docs-swagger.png
- ✅ 06-api-docs-redoc.png
- ✅ 11-api-endpoints.png
- ✅ 12-api-response.png

### 4. Manual Screenshots Required

#### Terminal Screenshots
```bash
# 07-cli-interface.png
python -m src.cli --help
# Take screenshot of terminal output

# 08-cli-output.png
python -m src.cli analytics courses
# Take screenshot of terminal output

# 10-docker-containers.png
docker-compose ps
# Take screenshot of terminal output
```

#### Diagram Exports

**09-architecture-diagram.png** - Architecture Diagram
- Option A: Use Mermaid Live Editor
  ```bash
  "$BROWSER" https://mermaid.live
  # Copy content from docs/architecture.mmd
  # Export as PNG → save to docs/images/09-architecture-diagram.png
  ```
- Option B: Docker (automated)
  ```bash
  docker run --rm -v "$(pwd)/docs:/data" minlag/mermaid-cli \
    mmdc -i /data/architecture.mmd -o /data/images/09-architecture-diagram.png \
    -w 1600 -H 900 -b transparent
  ```

**13-database-schema.png** - Database ERD
- Visit https://dbdiagram.io
- Import `docs/db/erd.dbml`
- Arrange layout
- Export as PNG → save to `docs/images/13-database-schema.png`

### 5. Verify All Screenshots
```bash
ls -1 docs/images/*.png | wc -l
# Should show 13 files

ls -1 docs/images/*.png
```

## Screenshot Checklist

- [ ] 01-dashboard-home.png (Streamlit main page)
- [ ] 02-analytics-page.png (Analytics with charts)
- [ ] 03-ai-insights.png (AI insights page)
- [ ] 04-automation-page.png (Automation tools)
- [ ] 05-api-docs-swagger.png (Swagger UI)
- [ ] 06-api-docs-redoc.png (ReDoc UI)
- [ ] 07-cli-interface.png (CLI help menu)
- [ ] 08-cli-output.png (CLI command output)
- [ ] 09-architecture-diagram.png (System architecture)
- [ ] 10-docker-containers.png (Docker ps output)
- [ ] 11-api-endpoints.png (API endpoint list)
- [ ] 12-api-response.png (API JSON response)
- [ ] 13-database-schema.png (Database ERD)

## Quality Guidelines

- Format: PNG
- Resolution: 1920x1080 (desktop), 1200x800 (terminal)
- Browser zoom: 100%
- Terminal: Light theme, readable fonts
- No sensitive data (passwords, keys, personal info)
- Clean UI state (no error messages unless intentional)

## Open Tabs for Manual Review
```bash
bash scripts/open_tabs.sh
```
