import json
import langfun as lf
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the generative AI model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def analyze_courses(courses_data):
    """
    Analyzes the scraped course data using langfun to generate summaries,
    key concepts, and insights for each course.

    Args:
        courses_data (list): A list of dictionaries, where each dictionary
            contains the title and description of a course.

    Returns:
        list: A list of dictionaries, where each dictionary contains the
            analyzed data for a course.
    """
    analyzed_courses = []
    for course in courses_data:
        # Generate a one-sentence summary of the course description.
        summary = lf.query(
            "Summarize the following course description in one sentence: {{description}}",
            lm=lf.llms.GeminiPro(),
            description=course['description']
        )

        # This is a placeholder for the key concepts and insights.
        # I will implement the logic to extract these in the next steps.
        key_concepts = []
        insights = ""

        analyzed_courses.append({
            'title': course['title'],
            'description': course['description'],
            'summary': str(summary),
            'key_concepts': key_concepts,
            'insights': insights,
        })
    return analyzed_courses


if __name__ == '__main__':
    with open('courses_data.json', 'r') as f:
        courses_data = json.load(f)

    analyzed_data = analyze_courses(courses_data)

    with open('openhpi-visualizer/analyzed_courses.json', 'w') as f:
        json.dump(analyzed_data, f, indent=4)
