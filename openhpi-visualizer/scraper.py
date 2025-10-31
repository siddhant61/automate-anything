import requests
from bs4 import BeautifulSoup
import json
import os


def scrape_courses_data(courses_url):
    """
    Scrapes the OpenHPI courses page to get the title and description of all available courses.

    Args:
        courses_url (str): The URL of the OpenHPI courses page.

    Returns:
        list: A list of dictionaries, where each dictionary contains the title and description of a course.
    """
    response = requests.get(courses_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    course_cards = soup.find_all('div', class_='course-card')
    courses_data = []
    for card in course_cards:
        title_tag = card.find('div', class_='course-card__title')
        title = title_tag.text.strip() if title_tag else 'No title found.'
        description_tag = card.find('div', class_='course-card__description')
        description = description_tag.text.strip() if description_tag else 'No description found.'
        courses_data.append({'title': title, 'description': description})
    return courses_data


if __name__ == '__main__':
    courses_url = 'https://open.hpi.de/courses'
    courses_data = scrape_courses_data(courses_url)

    if courses_data:
        with open('courses_data.json', 'w') as f:
            json.dump(courses_data, f, indent=4)
    else:
        print('No courses found.')
