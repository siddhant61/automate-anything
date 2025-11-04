---
name: OpenHPI Automator
description: Refactors and productionalizes the OpenHPI automation and analysis suite by unifying scripts into a modular, configurable, and robust application.
---

# My Agent: OpenHPI Automator Workflow

Always follow this structured workflow to refactor the project. The primary goals are to **eliminate hardcoding**, **unify the codebase**, and **build a scalable architecture** (API, DB, UI).

### 1. Evaluate the Given Task

Deconstruct the task by mapping it to the project's target architectural layers.

| Context | Focus Area | Project Example (File) |
| :--- | :--- | :--- |
| **Universal Context** (Overall Goal) | The complete **OpenHPI Automation Pipeline**: **Scrape $\rightarrow$ Store $\rightarrow$ Analyze $\rightarrow$ Automate $\rightarrow$ Present**. | Adding a new course report must integrate with the central database and be exposed via the API. |
| **Data Ingestion Layer** (Scraping/Parsing) | `requests`+`bs4` scrapers, Selenium scripts, `course_parser.py`. | Refactoring `data_scraper.py` from Selenium to `requests`. |
| **Persistence Layer** (Database) | Central database (e.g., SQLAlchemy models) that *replaces* all local CSV files. | Defining the `CourseStats` table and making `course_analytics.py` read from it. |
| **Automation Layer** (Write Actions) | Selenium-based scripts that perform platform actions. | `batch_enroll.py`, `page_updater.py`. |
| **Analysis Layer** (Analytics & AI) | `pandas`/`matplotlib` analytics, R scripts, `langfun` AI analysis. | `course_analytics.py`, `openhpi-visualizer/analysis.py`. |
| **Presentation Layer** (API & UI) | FastAPI backend, `plotly` visualizations, and the future UI. | `openhpi-visualizer/visualization.py`, new API endpoints. |
| **Core Context** (Config & CLI) | Configuration (`config.py`, `.env`), and the main CLI entry point. | `main.py` or `cli.py`. |

***

### 2. Audit the Present State of the Codebase

Conduct a targeted review of the *existing scripts* to identify logic that needs to be refactored *before* writing new code.

* **Hardcoding (Priority 1):** Identify any hardcoded credentials (`username`, `password`, `token`), file paths (`C:/Users/siddh/...`), or resource URLs (`/courses/qc-optimization2023`). **These must be replaced.**
* **Technology:** Check if the script uses `selenium` or `requests`. Selenium scripts are high-priority for replacement.
* **Data Flow:** Determine what data the script *consumes* (e.g., `emails.csv`) and *produces* (e.g., `course_data.csv`). This will inform the database model.
* **Configuration:** Check the `openhpi-visualizer` `.env` model. All new configuration must follow this pattern.
* **Selectors:** If auditing a Selenium script, find the brittle XPaths (`/html/body/...`) and identify more stable selectors (like `id` or `class`) to use in the refactored `requests`-based version.

***

### 3. Create an Organized Set of Sequential Tasks

Formulate a structured plan that migrates functionality from the old scripts to the new, unified architecture.

1.  **Define/Update Config:** Identify all hardcoded values from the script. Add new variables to `.env` and `config.py` to manage them (e.g., `HELPDESK_USERNAME`, `HELPDESK_PASSWORD`).
2.  **Define Database Models:** Define the `SQLAlchemy` (or other ORM) models needed for the data. (e.g., `User`, `Course`, `TeacherSurvey`).
3.  **Refactor Core Logic:** Create a new module (e.g., `src/automator/scraping.py` or `src/automator/analysis.py`). Copy the *logic* (not the hardcoded parts) from the old script into a new, parameterized function (e.g., `def scrape_course_stats(course_id: str) -> dict:`).
4.  **Implement Data Storage:** Modify the new function to write its results to the database instead of a CSV.
5.  **Build API/CLI Interface:** Create a new FastAPI endpoint (e.g., `POST /api/scrape/{course_id}`) or a `typer`/`click` command (e.g., `python run.py scrape {course_id}`) that calls your new function.
6.  **Create Test Plan:** Write a `pytest` test for the new function, using `pytest-mock` to mock the `requests` calls.
7.  **Deprecate Old Script:** Once fully migrated, delete the original script from the root directory.

***

### 4. Start Executing the Structured Tasks $\rightarrow$ Test $\rightarrow$ Refine

Execute the refactoring plan, following strict quality standards.

1.  **Execute & Test:** Implement the logic for the current subtask (e.g., refactoring `data_scraper.py`).
2.  **Enforce Quality Standards:**
    * **NO Hardcoding:** All credentials, tokens, and paths *must* be loaded from the `config.py` module, which loads from `.env`.
    * **Prefer `requests`:** Do not use Selenium unless it is impossible to achieve the goal with `requests.Session()`.
    * **Database First:** All data must be persisted to the central database. Do not use intermediate CSVs for data flow.
    * **Async (where appropriate):** Use `async/await` for I/O-bound tasks, especially in the FastAPI backend and for `httpx`-based scraping.
3.  **Refine & Complete:** Ensure the new, refactored module is integrated into the main application, tested, and the old script is removed.
