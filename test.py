import pandas as pd
import matplotlib.pyplot as plt
import ast

# Load the data
data = pd.read_csv("course_data.csv")

# Function to clean the value column
def clean_value(val):
    try:
        # Attempt to convert to list
        return ast.literal_eval(val)
    except:
        # Handle percentage values
        if "%" in str(val):
            return float(val.strip('%')) / 100  # Convert percentage to a proportion
        # Handle comma in numbers
        if "," in str(val):
            return int(val.replace(',', ''))
        # Handle NaN and other values
        return val

def clean_header(header):
    # Capitalize the first letter of each word
    return ' '.join([word.capitalize() for word in header.split()])

# Apply cleaning functions
data['value'] = data['value'].apply(clean_value)
data['header'] = data['header'].apply(clean_header)

data.to_csv("cleaned_course_data.csv", index=False)
data.head()  # Display cleaned data for verification
# print(data)

# Extract the unique course codes for user selection
course_codes = data['code'].unique().tolist()

# Extract the headers available for plotting
plots_headers = data[data['section'] == 'plots']['header'].unique().tolist()


def plot_single_course(course_code, header, data):
    """
    This function plots data for a single course based on the header provided.
    """
    course_data = data[(data['code'] == course_code) & (data['header'] == header)]

    if not course_data.empty:
        value = course_data['value'].iloc[0]

        # Check if the value is a list (indicative of plot data)
        if isinstance(value, list):
            x_values = [point['x'] for point in value]
            y_values = [point['y'] for point in value]

            # Plot
            plt.figure(figsize=(15, 7))
            plt.plot(x_values, y_values, marker='o')
            plt.title(f"{header} for {course_code}")
            plt.xlabel("Date")
            plt.ylabel(header)
            plt.xticks(x_values[::10], rotation=45)
            plt.grid(True, which="both", ls="--")
            plt.tight_layout()
            plt.show()
        else:
            print(f"The header '{header}' for course '{course_code}' does not have plot data.")
    else:
        print(f"Data for header '{header}' in course '{course_code}' not found.")


def plot_multiple_courses(course_codes, header, data):
    """
    Plot multiple course data for a given header.
    """
    plt.figure(figsize=(15, 8))

    for course_code in course_codes:
        course_data = data[(data['code'] == course_code) & (data['header'] == header)]
        if not course_data.empty:
            values_list = course_data['value'].iloc[0]
            if isinstance(values_list, list):
                # This is from the "plots" section
                y_values = [point['y'] if point['y'] is not None else 0 for point in values_list]
                x_values = list(range(0, len(y_values)*10, 10))  # 10-day intervals

                plt.plot(x_values, y_values, label=course_code)
            else:
                print(f"'{header}' is not a 'plots' type header for course code '{course_code}'.")
        else:
            print(f"'{header}' not found in data for course code '{course_code}'.")

    plt.title(f'Multiple Courses Data for {header}')
    plt.xlabel('Days since start')
    plt.ylabel(header)
    plt.legend()
    plt.grid(True)
    plt.show()


def compare_courses(course_codes, data):
    """
    Compare multiple courses based on their stats.
    """
    stats_headers = data['header'].unique().tolist()
    common_headers = []

    for header in stats_headers:
        if all(data[(data['code'] == course_code) & (data['header'] == header)].shape[0] > 0 for course_code in course_codes):
            common_headers.append(header)

    # Filter headers to only those which are numerical stats
    common_headers = [header for header in common_headers if
                      isinstance(data[data['header'] == header]['value'].iloc[0], (int, float))]

    # Group the headers in sets of 3
    grouped_headers = [common_headers[i:i + 3] for i in range(0, len(common_headers), 3)]

    for headers_set in grouped_headers:
        # Create a subplot for each group of 3 headers
        fig, axes = plt.subplots(1, len(headers_set), figsize=(15, 6), constrained_layout=True)

        for idx, header in enumerate(headers_set):
            values = []
            for course_code in course_codes:
                course_data = data[(data['code'] == course_code) & (data['header'] == header)]
                if not course_data.empty:
                    val = course_data['value'].iloc[0]
                    values.append(float(val) if isinstance(val, (int, float)) else 0)
                else:
                    values.append(0)

            if len(headers_set) > 1:
                axes[idx].bar(course_codes, values,
                              color=['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive',
                                     'cyan'][:len(course_codes)])
                axes[idx].set_title(header)
                axes[idx].set_xticks(course_codes)
                axes[idx].set_xlabel("Course Code")
                axes[idx].set_ylabel("Value")
            else:
                axes.bar(course_codes, values,
                         color=['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan'][
                                :len(course_codes)])
                axes.set_title(header)
                axes.set_xticks(course_codes)
                axes.set_xlabel("Course Code")
                axes.set_ylabel("Value")

        plt.suptitle("Comparison of Stats for Multiple Courses")
        plt.show()


# plot course stats
course_code = 'datascience2023'
header = 'Enrollments (total)'
course_codes = ['datascience2023', 'compliance2023', 'bayesian-statistics2023']
plot_single_course(course_code, header, data)
plot_multiple_courses(course_codes, "Enrollments (total)", data)
compare_courses(course_codes, data)



