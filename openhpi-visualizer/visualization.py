import json
import plotly.graph_objects as go

def visualize_data(courses_data):
    """
    Creates an interactive visualization of the course data using Plotly.

    Args:
        courses_data (list): A list of dictionaries, where each dictionary
            contains the title and description of a course.
    """
    course_titles = [course['title'] for course in courses_data]
    description_lengths = [len(course['description']) for course in courses_data]

    fig = go.Figure([go.Bar(x=course_titles, y=description_lengths)])
    fig.update_layout(
        title="Course Description Lengths",
        xaxis_title="Course Title",
        yaxis_title="Description Length (characters)",
    )
    fig.write_html("openhpi-visualizer/course_visualizations.html")

if __name__ == '__main__':
    with open('courses_data.json', 'r') as f:
        courses_data = json.load(f)

    visualize_data(courses_data)
