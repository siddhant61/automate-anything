from scraper import scrape_courses_data
from analysis import analyze_courses
from visualization import visualize_data

def main():
    """
    Orchestrates the entire workflow, from data scraping to analysis and visualization.
    """
    # Scrape the course data.
    courses_data = scrape_courses_data('https://open.hpi.de/courses')

    # Analyze the course data.
    # analyzed_data = analyze_courses(courses_data)

    # Visualize the course data.
    visualize_data(courses_data)

if __name__ == '__main__':
    main()
