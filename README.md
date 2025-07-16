# OpenHPI Automation Project

An automation suite for the OpenHPI platform, designed to streamline course management, user administration, and data analysis. This project includes scripts for scraping, parsing, and analyzing course data, as well as tools for automating user enrollment and notifications.

## Features

*   **Course Data Management:** Scripts for scraping, parsing, and processing course information from the OpenHPI platform.
*   **Quiz and Survey Automation:** Tools for transforming, uploading, analyzing, and comparing quiz and survey data.
*   **User and Course Analytics:** Generation of annual statistics and detailed analytics on course performance and user engagement.
*   **User Automation:** Scripts for batch user enrollment and assignment to survey groups.
*   **System Integration:** Integration with a helpdesk system for automated notifications based on user activity.

## Project Structure

The project is composed of several Python and R scripts, each responsible for a specific aspect of the automation process:

| File                          | Description                                                                                             |
| ----------------------------- | ------------------------------------------------------------------------------------------------------- |
| `main.py`                     | The main entry point for running the data analysis and visualization workflows.                           |
| `course_scraper.py`           | Scrapes course data from the OpenHPI platform.                                                          |
| `data_scraper.py`             | A more general data scraper for the platform.                                                           |
| `fetch_course_data.py`        | Fetches specific course data based on given parameters.                                                 |
| `course_parser.py`            | Parses raw scraped data into a structured format.                                                       |
| `transform_quiz.py`           | Transforms quiz data into a consistent format for processing.                                           |
| `quiz_uploader.py`            | Uploads quizzes to the OpenHPI platform.                                                                |
| `quiz_analysis.py`            | Analyzes quiz results to generate insights.                                                             |
| `quiz_comparison.py`          | Compares quiz results over time or between different courses.                                           |
| `course_analytics.py`         | Provides detailed analytics on course performance.                                                      |
| `annual_stats.Rmd`            | An R Markdown file for generating annual statistics.                                                    |
| `batch_enroll.py`             | Performs batch enrollment of users into courses.                                                        |
| `survey_group.py`             | Assigns users to groups for surveys.                                                                    |
| `helpdesk_notifier.py`        | Sends notifications to a helpdesk system based on specific events.                                      |
| `page_updater.py`             | Updates external pages with new information from the platform.                                          |
| `test.py`                     | Contains tests for the various components of the automation suite.                                      |

## Getting Started

To get started with this project, you will need to have Python and R installed on your system. You will also need to install the required dependencies for each script.

### Prerequisites

*   Python 3.x
*   R
*   Required Python packages can be found in the import statements of each script.
*   Required R packages can be found in the `annual_stats.Rmd` file.

### Usage

The `main.py` script serves as the primary entry point for the data analysis workflow. To run the analysis, execute the following command:

```bash
python main.py
```

Other scripts can be run individually as needed. For example, to scrape course data, you can run:

```bash
python course_scraper.py
```

Make sure to configure any necessary API keys or credentials in an `.env` file in the root of the project. 