# OpenHPI Visualizer

This project provides a suite of tools for scraping, analyzing, and visualizing data from the OpenHPI platform. It's designed to be a stable, open-source solution for creating interactive visualizations, dashboards, summaries, reports, and short visual story-driven explainers for the content of any OpenHPI course.

## Features

*   **Data Scraping:** A robust and configurable scraper for collecting publicly available data from any OpenHPI course.
*   **AI-Powered Analysis:** An analysis module that uses Google's `langfun` and `langextract` libraries to identify key concepts, generate insights, and create a narrative from the scraped data.
*   **Interactive Visualizations:** A visualization module that uses Plotly to create interactive charts, graphs, and dashboards that can be easily shared as HTML files.
*   **Integrated Pipeline:** A cohesive and automated workflow that orchestrates the entire process, from data scraping to analysis and visualization.

## Getting Started

To get started with this project, you will need to have Python 3.x installed on your system. You will also need to install the required dependencies.

### Prerequisites

*   Python 3.x
*   Pip

### Installation

1.  Clone this repository to your local machine:

    ```bash
    git clone https://github.com/your-username/openhpi-visualizer.git
    ```
2.  Navigate to the project directory:

    ```bash
    cd openhpi-visualizer
    ```
3.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Usage

To run the entire pipeline, execute the following command:

```bash
python main.py --course-url <course_url>
```

Replace `<course_url>` with the URL of the OpenHPI course you want to analyze. The output will be an HTML file containing the interactive visualizations.
