import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


# Step 1: Load and Clean Data
def load_and_clean_data(filepath):
    data = pd.read_csv(filepath)

    # Convert date columns to datetime and handle timezones if necessary
    date_columns = ['start_date', 'display_start_date', 'end_date', 'course_middle_date']
    for col in date_columns:
        data[col] = pd.to_datetime(data[col], errors='coerce', utc=True)  # Ensure UTC is used

    # Convert boolean columns to integers
    bool_columns = ['hidden', 'auto_calculate_course_middle']
    for col in bool_columns:
        data[col] = data[col].astype(int)

    # Fill NaN values in numeric columns with 0 (assuming missing means no records)
    numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
    data[numeric_cols] = data[numeric_cols].fillna(0)

    return data


# Step 2: Summary Statistics
def summary_statistics(data):
    return data.describe()


# Step 3: Data Visualization
def visualize_data(data):
    # Distribution of Course Status
    plt.figure(figsize=(10, 5))
    sns.countplot(x='status', data=data)
    plt.title('Distribution of Course Status')
    plt.xlabel('Status')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.show()

    # Courses Start Date over Time (Timeline)
    plt.figure(figsize=(12, 6))
    data['start_date'].dropna().dt.tz_convert(None).dt.to_period('M').value_counts().sort_index().plot(kind='bar')
    plt.title('Course Start Dates Over Time')
    plt.xlabel('Month-Year')
    plt.ylabel('Number of Courses Started')
    plt.xticks(rotation=90)
    plt.show()

    # Engagement and Achievement Metrics Analysis
    engagement_cols = ['topics', 'collab_space_posts', 'helpdesk_tickets']
    for col in engagement_cols:
        plt.figure()
        data[col].hist(bins=20)
        plt.title(f'Histogram of {col} - Engagement Metrics')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        plt.grid(False)
        plt.show()


# Step 4: Correlation Analysis
def correlation_analysis(data):
    # Selecting relevant columns for correlation
    relevant_cols = ['topics', 'collab_space_posts', 'helpdesk_tickets', 'issued_badges']
    corr_matrix = data[relevant_cols].corr()
    sns.heatmap(corr_matrix, annot=True)
    plt.title('Correlation Matrix of Engagement and Achievement Metrics')
    plt.show()


# Main Function to run the analysis
def main():
    filepath = 'D:/course_data/OverallCourseSummaryReport.csv'
    data = load_and_clean_data(filepath)
    print(summary_statistics(data))
    visualize_data(data)
    correlation_analysis(data)


if __name__ == "__main__":
    main()

