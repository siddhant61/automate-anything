import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def fetch_course_data(url):
    try:
        # Send a request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content of the page with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the course description
        course_description = soup.find('div', class_='col-md-12 course-description mt20')
        course_description_text = course_description.get_text(
            strip=True) if course_description else "Description not found."

        # Extract the course start and end dates
        start_date_div = soup.find('div', class_='enrollment-statistics__row', attrs={'data-type': 'course_start'})
        end_date_div = soup.find('div', class_='enrollment-statistics__row', attrs={'data-type': 'course_end'})

        start_date_text = start_date_div.find('div', class_='enrollment-statistics__date-value').get_text(
            strip=True) if start_date_div else "Start date not found."
        end_date_text = end_date_div.find('div', class_='enrollment-statistics__date-value').get_text(
            strip=True) if end_date_div else "End date not found."

        # Convert dates to datetime objects
        try:
            start_date = datetime.strptime(start_date_text, "%B %d, %Y")
        except ValueError:
            start_date = None

        try:
            end_date = datetime.strptime(end_date_text, "%B %d, %Y")
        except ValueError:
            end_date = None

        # Calculate the duration in weeks
        if start_date and end_date:
            duration_days = (end_date - start_date).days
            duration_weeks = max(duration_days // 7, 1)  # Ensure at least 1 week
        else:
            duration_weeks = None

        return {
            "course_description": course_description_text,
            "course_start_date": start_date_text,
            "course_end_date": end_date_text,
            "course_duration_weeks": duration_weeks
        }

    except requests.RequestException as e:
        return {
            "course_description": f"Error fetching page: {e}",
            "course_start_date": None,
            "course_end_date": None,
            "course_duration_weeks": None
        }


def update_course_descriptions(csv_file):
    # Load the CSV file into a DataFrame with the specified encoding
    df = pd.read_csv(csv_file, encoding='ISO-8859-1')

    # Apply the function to fetch descriptions and other data for each course link in the DataFrame
    course_data = df['course page'].apply(fetch_course_data)

    # Create separate columns for each piece of data
    df['course description'] = course_data.apply(lambda x: x['course_description'])
    df['course start date'] = course_data.apply(lambda x: x['course_start_date'])
    df['course end date'] = course_data.apply(lambda x: x['course_end_date'])
    df['course duration in weeks'] = course_data.apply(lambda x: x['course_duration_weeks'])

    # Save the updated DataFrame back to the CSV
    df.to_csv(csv_file, index=False)
    print("CSV file has been updated with course descriptions, start and end dates, and duration in weeks.")


# Specify the path to your CSV file
csv_file_path = 'C:/Users/siddh/Desktop/courses_competences.csv'

# Call the function to update the CSV file with course descriptions and other data
update_course_descriptions(csv_file_path)
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def fetch_course_data(url):
    try:
        # Send a request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content of the page with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the course description
        course_description = soup.find('div', class_='col-md-12 course-description mt20')
        course_description_text = course_description.get_text(
            strip=True) if course_description else "Description not found."

        # Extract the course start and end dates
        start_date_div = soup.find('div', class_='enrollment-statistics__row', attrs={'data-type': 'course_start'})
        end_date_div = soup.find('div', class_='enrollment-statistics__row', attrs={'data-type': 'course_end'})

        start_date_text = start_date_div.find('div', class_='enrollment-statistics__date-value').get_text(
            strip=True) if start_date_div else "Start date not found."
        end_date_text = end_date_div.find('div', class_='enrollment-statistics__date-value').get_text(
            strip=True) if end_date_div else "End date not found."

        # Convert dates to datetime objects
        try:
            start_date = datetime.strptime(start_date_text, "%B %d, %Y")
        except ValueError:
            start_date = None

        try:
            end_date = datetime.strptime(end_date_text, "%B %d, %Y")
        except ValueError:
            end_date = None

        # Calculate the duration in weeks
        if start_date and end_date:
            duration_days = (end_date - start_date).days
            duration_weeks = max(duration_days // 7, 1)  # Ensure at least 1 week
        else:
            duration_weeks = None

        return {
            "course_description": course_description_text,
            "course_start_date": start_date_text,
            "course_end_date": end_date_text,
            "course_duration_weeks": duration_weeks
        }

    except requests.RequestException as e:
        return {
            "course_description": f"Error fetching page: {e}",
            "course_start_date": None,
            "course_end_date": None,
            "course_duration_weeks": None
        }


def update_course_descriptions(csv_file):
    # Load the CSV file into a DataFrame with the specified encoding
    df = pd.read_csv(csv_file, encoding='ISO-8859-1')

    # Apply the function to fetch descriptions and other data for each course link in the DataFrame
    course_data = df['course page'].apply(fetch_course_data)

    # Create separate columns for each piece of data
    df['course description'] = course_data.apply(lambda x: x['course_description'])
    df['course start date'] = course_data.apply(lambda x: x['course_start_date'])
    df['course end date'] = course_data.apply(lambda x: x['course_end_date'])
    df['course duration in weeks'] = course_data.apply(lambda x: x['course_duration_weeks'])

    # Save the updated DataFrame back to the CSV
    df.to_csv(csv_file, index=False)
    print("CSV file has been updated with course descriptions, start and end dates, and duration in weeks.")


# Specify the path to your CSV file
csv_file_path = 'C:/Users/siddh/Desktop/courses_competences.csv'

# Call the function to update the CSV file with course descriptions and other data
update_course_descriptions(csv_file_path)
