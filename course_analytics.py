import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# Define the fixed periods
fixed_periods = {
    '2021': ('2021-02-01', '2021-06-30'),
    '2022': ('2022-03-01', '2022-06-30'),
    '2023': ('2023-01-01', '2023-06-30'),
    '2024': ('2024-03-01', '2024-06-30')
}


# Function to load and prepare data
def load_and_prepare_data(file_paths, course_name):
    combined_data = pd.DataFrame()
    for file_path in file_paths:
        # Extract the year from the filename
        year = Path(file_path).stem.split('-')[-1][-4:]
        data = pd.read_csv(file_path)
        data.columns = [col.lower().replace(" ", "_") for col in data.columns]
        data['enrollment_date'] = pd.to_datetime(data['enrollment_date'], errors='coerce')
        data['year'] = int(year)
        data['course'] = course_name
        combined_data = pd.concat([combined_data, data])
    return combined_data

# Calculate Metrics
def calculate_metrics(group):
    metrics = {}
    metrics['certificates'] = group[(group['confirmation_of_participation'] == True) | (group['record_of_achievement'] == True)].groupby(['year', 'course']).size()
    metrics['average_session_length'] = group.groupby(['year', 'course'])['avg_session_duration'].mean()
    metrics['items_visited_percentage'] = group.groupby(['year', 'course'])['items_visited_percentage'].mean()
    metrics['completion_rates'] = group.groupby(['year', 'course'])['course_completed'].apply(lambda x: (x == True).sum() / len(x))
    metrics['graded_quiz_performance'] = group.groupby(['year', 'course'])['graded_quiz_performance'].mean()*100
    metrics['ungraded_quiz_performance'] = group.groupby(['year', 'course'])['ungraded_quiz_performance'].mean()*100
    return metrics

# File paths
java_files = [
    'C:/Users/siddh/Desktop/openHPI/reports/Java/javaeinstieg-schule2021.csv',
    'C:/Users/siddh/Desktop/openHPI/reports/Java/javaeinstieg-schule2022.csv',
    'C:/Users/siddh/Desktop/openHPI/reports/Java/javaeinstieg-schule2023.csv',
    'C:/Users/siddh/Desktop/openHPI/reports/Java/javaeinstieg-schule2024.csv'
]

python_files = [
    'C:/Users/siddh/Desktop/openHPI/reports/Python/pythonjunior-schule2021.csv',
    'C:/Users/siddh/Desktop/openHPI/reports/Python/pythonjunior-schule2022.csv',
    'C:/Users/siddh/Desktop/openHPI/reports/Python/pythonjunior-schule2023.csv',
    'C:/Users/siddh/Desktop/openHPI/reports/Python/pythonjunior-schule2024.csv'
]

# Load and prepare data
java_course_data = load_and_prepare_data(java_files, 'Java')
python_course_data = load_and_prepare_data(python_files, 'Python')

# Combine data for both courses
combined_data = pd.concat([java_course_data, python_course_data]).copy()

# Remove timezone information
combined_data['enrollment_date'] = combined_data['enrollment_date'].dt.tz_localize(None)
combined_data['enrollment_month'] = combined_data['enrollment_date'].dt.to_period('M')

# Drop-Out Conditions
drop_out_conditions = (combined_data['sessions'] < 2) & (combined_data['total_session_duration'] < 600)
# Filter out dropped-out users
filtered_combined_data = combined_data[~drop_out_conditions]

# Filter data within fixed periods
def filter_fixed_periods(data, fixed_periods):
    filtered_data = pd.DataFrame()
    for year, (start_date, end_date) in fixed_periods.items():
        period_data = data[(data['enrollment_date'] >= start_date) & (data['enrollment_date'] <= end_date)]
        filtered_data = pd.concat([filtered_data, period_data])
    return filtered_data

filtered_data = filter_fixed_periods(filtered_combined_data, fixed_periods)

# Grouping data by course, month, and year for plotting
monthly_enrollments = filtered_data.groupby(
    ['year', 'enrollment_month', 'course']).size().unstack().fillna(0)

# Drop-Out Rates
drop_out_rates = combined_data[drop_out_conditions].groupby(['year', 'course', 'enrollment_month']).size() / combined_data.groupby(['year', 'course', 'enrollment_month']).size() * 100
drop_out_rates = drop_out_rates.unstack(level=1).fillna(0)

# First-Time Users
first_time_users = filtered_data[filtered_data['first_enrollment'] == True]
non_first_time_users = filtered_data[filtered_data['first_enrollment'] == False]
first_time_metrics = calculate_metrics(first_time_users)
non_first_time_metrics = calculate_metrics(non_first_time_users)

# Users with Certificates
certificates = filtered_data[(filtered_data['confirmation_of_participation'] == True) | (filtered_data['record_of_achievement'] == True)].groupby(['year', 'course']).size()

# Average Session Length
average_session_length = filtered_data.groupby(['year', 'course'])['avg_session_duration'].mean()

# Items Visited Percentage
first_time_visits = filtered_data[filtered_data['first_enrollment'] == True]['items_visited_percentage'].mean()
non_first_time_visits = filtered_data[filtered_data['first_enrollment'] == False]['items_visited_percentage'].mean()

# Extracting columns between points_percentage and course_code
progression_columns = filtered_data.loc[:, 'points_percentage':'course_code'].columns

# Convert progression columns to numeric
filtered_data[progression_columns] = filtered_data[progression_columns].apply(pd.to_numeric, errors='coerce')

# Most Visited Items
most_visited_items = filtered_data[progression_columns].apply(pd.Series.mode)

# Language Preferences
language_distribution = filtered_data.groupby(['course', 'year', 'language']).size().unstack().fillna(0)

# Top 5 Countries
top_countries = filtered_data.groupby(['course', 'year', 'top_country_name']).size().unstack().fillna(0).apply(lambda x: x.nlargest(5), axis=1)

# Quiz Performance
graded_quiz_performance = filtered_data.groupby(['year', 'course'])['graded_quiz_performance'].mean()
ungraded_quiz_performance = filtered_data.groupby(['year', 'course'])['ungraded_quiz_performance'].mean()

# Completion Rates
completion_rates = filtered_data.groupby(['year', 'course'])['course_completed'].apply(lambda x: (x == True).sum() / len(x))
print(completion_rates)

# User Progression
first_time_progression = filtered_data[filtered_data['first_enrollment'] == True][progression_columns].mean(axis=1)
non_first_time_progression = filtered_data[filtered_data['first_enrollment'] == False][progression_columns].mean(axis=1)

# Plotting
colors = {'Java': '#1f77b4', 'Python': '#ff7f0e'}


# Function to create subplots for a given set of years
def create_enrollment_subplots(years, monthly_enrollments, fig_title):
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 5), sharey=True)
    fig.suptitle(fig_title, fontsize=16)

    for i, year in enumerate(years):
        ax = axes[i]
        year_data = monthly_enrollments.loc[year]

        # Define the fixed range
        start_period = pd.Period(f'Jan-{year}', freq='M')
        end_period = pd.Period(f'Dec-{int(year)}', freq='M')
        periods_range = pd.period_range(start=start_period, end=end_period, freq='M')

        # Filter data within the defined range
        year_data = year_data.reindex(periods_range, fill_value=0)

        # Plot side-by-side bars for Java and Python
        bars = year_data.plot(kind='bar', colormap='viridis', ax=ax, position=0.8, width=0.4)

        ax.set_title(f'Jahr: {year}', fontsize=14)
        ax.set_xlabel('Monat', fontsize=12)
        ax.set_ylabel('Anzahl der Einschreibungen', fontsize=12)
        ax.legend(title='Kurs', fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Set x-axis labels to include months of that year only
        ax.set_xticks(range(len(year_data.index)))
        ax.set_xticklabels([f"{date.strftime('%b')}\n{date.year}" for date in year_data.index], rotation=45)

        # Label numbers for all bars
        for bar in bars.containers:
            ax.bar_label(bar, fmt='%.0f', label_type='edge', fontsize=10)

        # Highlight peak periods for Java and Python on opposite sides
        if 'Java' in year_data.columns:
            java_data = year_data['Java']
            peak_enrollment_month_idx = java_data.argmax()
            peak_enrollment_month = java_data.index[peak_enrollment_month_idx]
            peak_value = java_data.max()
            ax.annotate(f'Höhepunkt\nJava\n{peak_value}', xy=(peak_enrollment_month_idx-0.2, peak_value),
                        xytext=(peak_enrollment_month_idx - 0.7, peak_value + 10),
                        ha='right',
                        arrowprops=dict(facecolor='black', shrink=0.02))

        if 'Python' in year_data.columns:
            python_data = year_data['Python']
            peak_enrollment_month_idx = python_data.argmax()
            peak_enrollment_month = python_data.index[peak_enrollment_month_idx]
            peak_value = python_data.max()
            ax.annotate(f'Höhepunkt\nPython\n{peak_value}', xy=(peak_enrollment_month_idx, peak_value),
                        xytext=(peak_enrollment_month_idx + 0.5, peak_value + 1),
                        ha='left',
                        arrowprops=dict(facecolor='black', shrink=0.02))

    # Adjust layout
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()



# Create subplots for (2021, 2022) and (2023, 2024)
# create_enrollment_subplots([2021, 2022], monthly_enrollments, 'Monatliche Einschreibungstrends für Java- und Python-Schulkurse (2021-2022)')
# create_enrollment_subplots([2023, 2024], monthly_enrollments, 'Monatliche Einschreibungstrends für Java- und Python-Schulkurse (2023-2024)')


# Function to create subplots for drop-out rates
def create_drop_out_subplots(years, drop_out_rates, fig_title):
    fig, axes = plt.subplots(nrows=1, ncols=len(years), figsize=(15, 5), sharey=True)
    fig.suptitle(fig_title, fontsize=16)

    for i, year in enumerate(years):
        ax = axes[i]
        year_data = drop_out_rates.loc[year]
        start_period = pd.Period(f'Jan-{year}', freq='M')
        end_period = pd.Period(f'Dec-{year}', freq='M')
        periods_range = pd.period_range(start=start_period, end=end_period, freq='M')

        year_data = year_data.reindex(periods_range, fill_value=0)
        year_data.plot(kind='line', marker='o', linestyle='-', colormap='viridis', ax=ax)
        ax.set_title(f'Year: {year}', fontsize=14)
        ax.set_xlabel('Month')
        ax.set_ylabel('Drop-out Rate (%)')
        ax.legend(title='Course')
        ax.grid(axis='both', linestyle='--', alpha=0.7)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

# Create subplots for drop-out rates
# create_drop_out_subplots([2021, 2022], drop_out_rates, 'Yearly Drop-out Trends for Java and Python Courses (2021-2022)')
# create_drop_out_subplots([2023, 2024], drop_out_rates, 'Yearly Drop-out Trends for Java and Python Courses (2023-2024)')


# Function to plot language distribution
def plot_language_preferences_by_year(years, language_distribution, title):
    num_years = len(years)
    num_courses = 2  # Assuming two courses, Java and Python
    fig, axes = plt.subplots(num_years, num_courses, figsize=(14, 8 * num_years))  # Layout for multiple years
    fig.suptitle(title, fontsize=16)

    for i, year in enumerate(years):
        for j, course in enumerate(['Java', 'Python']):
            ax = axes[i][j] if num_years > 1 else axes[j]

            # Extract the language data for the specified year and course
            try:
                data = language_distribution.loc[(course, year)]
                data_sum = data.sum()  # Total count of all language entries
                # Calculate 'de', 'en', and 'others'
                de = data.get('de', 0)
                en = data.get('en', 0)
                others = data_sum - (de + en)
                # Create series and conditionally include 'others'
                data_dict = {'de': de, 'en': en}
                if others > 0:
                    data_dict['others'] = others
                data = pd.Series(data_dict)
            except KeyError:
                data = pd.Series([0, 0], index=['de', 'en'])

            # Check if data contains only zeros
            if data.sum() == 0:
                ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
                ax.set_axis_off()  # Hide axes if no data
                continue

            # Plotting the pie chart
            data.plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax, colors=plt.get_cmap('tab20').colors)
            ax.set_title(f'{course} Course, {year}', fontsize=14)
            ax.set_ylabel('')  # Remove the y-axis label for clarity

    plt.subplots_adjust(hspace=0.5)  # Adjust the space between the subplots
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()


# plot_language_preferences_by_year([2021, 2022], language_distribution, 'Language Preferences by Year')
# plot_language_preferences_by_year([2023, 2024], language_distribution, 'Language Preferences by Year')

# Geographical Distribution
def autopct_format(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}% ({v:d})'.format(p=pct,v=val) if pct > 10 else ''
    return my_autopct

def plot_geographical_distribution_by_year(years, top_countries, title):
    num_years = len(years)
    fig, axes = plt.subplots(num_years * 2, 1, figsize=(18, 12 * num_years))  # Adjust figure size for better visualization
    fig.suptitle(title, fontsize=16)

    # Combine all countries data to determine the most common ones for a consistent color map
    combined_countries = pd.concat([top_countries.loc[(course, year)] for year in years for course in ['Java', 'Python']])
    combined_countries = combined_countries.groupby('top_country_name').sum()  # Correct column name here
    top_common_countries = combined_countries.nlargest(10).index
    color_map = plt.get_cmap('tab20')(np.linspace(0, 1, len(top_common_countries)))
    color_dict = dict(zip(top_common_countries, color_map))

    if num_years == 1:
        axes = [axes]  # Adjust axes to be iterable if there's only one year

    for i, year in enumerate(years):
        for j, course in enumerate(['Java', 'Python']):
            ax = axes[i * 2 + j]  # Calculate the index for the subplot

            # Extract and sort data for the specified year and course
            try:
                data = top_countries.loc[(course, year)].sort_values(ascending=False)
                # Combine small proportions into 'Others'
                others = data[data < data.sum() * 0.02].sum()
                data = data[data >= data.sum() * 0.02]
                if others > 0:
                    data['Others'] = others
                # Ensure only top common countries and others are plotted with predefined colors
                data = data.loc[[country for country in data.index if country in top_common_countries or country == 'Others']]
            except KeyError:
                data = pd.Series([])  # Handle case where no data is available

            # Plotting logic for pie charts
            if data.empty:
                ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
                ax.set_axis_off()  # Hide axes if no data
                continue

            colors = [color_dict.get(country, 'gray') for country in data.index]  # Get colors from dictionary, default to 'gray'
            explode = [0.1 if country == data.max() else 0 for country in data]  # Explode the largest piece
            data.plot(kind='pie', ax=ax, autopct=autopct_format(data), startangle=90, colors=colors, explode=explode, labels=None)
            ax.set_ylabel('')
            ax.set_title(f'{course} Course, {year}', fontsize=14)
            ax.legend(labels=data.index, title="Countries", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

# plot_geographical_distribution_by_year([2021, 2022], top_countries, 'Top Countries Represented in Courses Over Years')
# plot_geographical_distribution_by_year([2023, 2024], top_countries, 'Top Countries Represented in Courses Over Years')


# Function to create subplots for first-time vs non-first-time users
def create_comparison_subplots(years, first_time_metrics, non_first_time_metrics, fig_title):
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15, 15), sharey=False)
    fig.suptitle(fig_title, fontsize=16)

    metrics = ['certificates', 'average_session_length', 'items_visited_percentage', 'completion_rates',
               'graded_quiz_performance', 'ungraded_quiz_performance']
    metric_titles = ['Certificates', 'Average Session Length', 'Items Visited Percentage', 'Completion Rates',
                     'Graded Quiz Performance', 'Ungraded Quiz Performance']
    colors = ['#1f77b4', '#ff7f0e']
    width = 0.35  # Width of the bars

    for i, metric in enumerate(metrics):
        ax = axes[i // 2, i % 2]
        ind = np.arange(len(first_time_metrics[metric]))
        first_time_data = first_time_metrics[metric].loc[years[0]]
        for j, year in enumerate(years):
            if year == '2024' and metric == 'certificates':
                continue
            else:
                if year in first_time_metrics[metric].index:
                    first_time_data = first_time_metrics[metric].loc[year]
                    non_first_time_data = non_first_time_metrics[metric].loc[year]
                    ind = np.arange(len(first_time_data))  # the label locations
                    offset = j * width  # position offset for this year's bars

                    ax.bar(ind + offset, first_time_data, width=width, label=f'{year} New Users', color=colors[0],
                           alpha=0.6)
                    ax.bar(ind + offset + width, non_first_time_data, width=width, label=f'{year} Old Users',
                           color=colors[1], alpha=0.6)

        ax.set_title(metric_titles[i])
        ax.set_xlabel('Course')
        ax.set_ylabel(metric_titles[i])
        ax.set_xticks(ind + width * (len(years) - 1) / 2)
        ax.set_xticklabels(first_time_data.index, rotation=45)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()


# Create subplots for the specified years
# create_comparison_subplots([2021], first_time_metrics, non_first_time_metrics,
#                            'Comparison of New vs Old Users')
# create_comparison_subplots([2022], first_time_metrics, non_first_time_metrics,
#                            'Comparison of New vs Old Users')
# create_comparison_subplots([2023], first_time_metrics, non_first_time_metrics,
#                            'Comparison of New vs Old Users')
# create_comparison_subplots([2024], first_time_metrics, non_first_time_metrics,
#                            'Comparison of New vs Old Users')


# Plot Combined Enrollments and Drop-Out Rates
def plot_combined_metrics(years, enrollments, drop_outs, fig_title, start_month='Feb', end_month='Jun'):
    fig, axes = plt.subplots(len(years), 1, figsize=(15, 10 * len(years)))
    fig.suptitle(fig_title, fontsize=16)

    colors = {'Java': '#1f77b4', 'Python':  '#ff7f0e'}

    for i, year in enumerate(years):
        ax1 = axes[i]
        year_data_enrollments = enrollments.loc[year]
        year_data_drop_outs = drop_outs.loc[year]

        # Define the period range for the subset of the year
        start_period = pd.Period(f'{start_month}-{year}', freq='M')
        end_period = pd.Period(f'{end_month}-{year}', freq='M')
        periods_range = pd.period_range(start=start_period, end=end_period, freq='M')

        # Filter data within the defined range
        year_data_enrollments = year_data_enrollments.reindex(periods_range, fill_value=0)
        year_data_drop_outs = year_data_drop_outs.reindex(periods_range, fill_value=0)

        # Convert PeriodIndex to month names
        month_labels = [date.strftime('%b') for date in year_data_enrollments.index]
        year_data_enrollments.index = month_labels
        year_data_drop_outs.index = month_labels

        ax2 = ax1.twinx()

        # Plot enrollments
        year_data_enrollments.plot(kind='bar', ax=ax1, position=0.8, width=0.4,
                                   color=[colors[col] for col in year_data_enrollments.columns], alpha=0.7)

        # Plot drop-out rates
        for course in year_data_drop_outs.columns:
            ax2.plot(year_data_drop_outs.index, year_data_drop_outs[course], marker='o', linestyle='-',
                     color=colors[course], label=f'{course} Drop-Out Rate')

        ax1.set_title(f'Year: {year}', fontsize=14)
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Enrollments')
        ax2.set_ylabel('Drop-Out Rate (%)')

        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        ax2.grid(axis='y', linestyle='--', alpha=0.7)

        # Set x-axis labels to be horizontal
        ax1.set_xticklabels(month_labels, rotation=0)

    # Adjust layout to increase the gap between subplots
    plt.subplots_adjust(hspace=0.5)  # Further increased hspace value
    plt.show()


# plot_combined_metrics([2021,2022], monthly_enrollments, drop_out_rates,
#                       'Combined Enrollments and Drop-Out Rates')
# plot_combined_metrics([2023,2024], monthly_enrollments, drop_out_rates,
#                       'Combined Enrollments and Drop-Out Rates')


def plot_metrics_for_year(year, enrollments, drop_outs, fig_title, start_month='Mar', end_month='Jun'):
    fig, ax1 = plt.subplots(figsize=(15, 10))
    fig.suptitle(fig_title, fontsize=16)

    colors = {'Java': '#1f77b4', 'Python': '#ff7f0e'}

    year_data_enrollments = enrollments.loc[year]
    year_data_drop_outs = drop_outs.loc[year]

    # Define the period range for the subset of the year
    start_period = pd.Period(f'{start_month}-{year}', freq='M')
    end_period = pd.Period(f'{end_month}-{year}', freq='M')
    periods_range = pd.period_range(start=start_period, end=end_period, freq='M')

    # Filter data within the defined range
    year_data_enrollments = year_data_enrollments.reindex(periods_range, fill_value=0)
    year_data_drop_outs = year_data_drop_outs.reindex(periods_range, fill_value=0)

    # Convert PeriodIndex to month names
    month_labels = [date.strftime('%b') for date in year_data_enrollments.index]
    year_data_enrollments.index = month_labels
    year_data_drop_outs.index = month_labels

    ax2 = ax1.twinx()

    # Plot enrollments
    year_data_enrollments.plot(kind='bar', ax=ax1, position=0.8, width=0.4,
                               color=[colors[col] for col in year_data_enrollments.columns], alpha=0.7)

    # Plot drop-out rates
    for course in year_data_drop_outs.columns:
        ax2.plot(year_data_drop_outs.index, year_data_drop_outs[course], marker='o', linestyle='-',
                 color=colors[course], label=f'{course} Drop-Out Rate')

    ax1.set_title(f'Year: {year}', fontsize=14)
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Enrollments')
    ax2.set_ylabel('Drop-Out Rate (%)')

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    # Set x-axis labels to be horizontal
    ax1.set_xticklabels(month_labels, rotation=0)

    plt.tight_layout(rect=[0, 0.01, 1, 0.95])
    plt.show()

# plot_metrics_for_year(2021, monthly_enrollments, drop_out_rates, 'Metrics for 2021', start_month='Feb', end_month='Jun')

years = [2021, 2022, 2023, 2024]
fig_title = "Course Metrics"

for year in years:
    plot_metrics_for_year(year, monthly_enrollments, drop_out_rates, fig_title)

def plot_certificates_vs_session_length_and_completion_rates(certificates, average_session_length, completion_rates):
    fig, ax1 = plt.subplots(figsize=(15, 7))

    # Plot the base bars
    certificates.plot(kind='bar', ax=ax1, position=0.8, width=0.4,
                      color=[colors.get(course, 'blue') for course in certificates.index.get_level_values('course')],
                      alpha=0.7)

    # Add the overlay for completion rates
    for idx, bar in enumerate(ax1.patches):
        height = bar.get_height()
        completion_rate = completion_rates.iloc[idx]
        hatch_height = height * completion_rate
        hatch_rect = plt.Rectangle((bar.get_x(), 0), bar.get_width(), hatch_height, fill=False, hatch='/',
                                   edgecolor='black', linewidth=0)
        ax1.add_patch(hatch_rect)
        ax1.annotate(f'{completion_rate:.0%}', (bar.get_x() + bar.get_width() / 2., hatch_height), ha='center', va='center',
                     xytext=(0, 0), textcoords='offset points')

    ax2 = ax1.twinx()
    average_session_length.plot(kind='line', marker='o', ax=ax2, color='green', alpha=0.7, linestyle='--')

    ax1.set_title('Certificate Issuance vs Session Length and Completion Rates')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of Certificates')
    ax2.set_ylabel('Session Length (s)')

    # Adding proxy artist for completion rate in the legend
    completion_rate_patch = mpatches.Patch(facecolor='none', edgecolor='black', hatch='/', label='Completion Rate')
    ax1.legend(handles=[completion_rate_patch], loc='upper left')
    ax2.legend(loc='upper right')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # Set x-axis labels to be horizontal
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)

    plt.tight_layout(rect=[0, 0.01, 1, 0.95])
    plt.show()


def plot_session_duration_vs_quiz_performance(average_session_length, graded_quiz_performance,
                                              ungraded_quiz_performance):
    fig, ax1 = plt.subplots(figsize=(15, 7))

    average_session_length.plot(kind='bar', ax=ax1, position=0.8, width=0.4,
                                color=[colors.get(course, 'blue') for course in
                                       average_session_length.index.get_level_values('course')], alpha=0.7)
    ax2 = ax1.twinx()
    graded_quiz_performance.plot(kind='line', marker='o', ax=ax2, color='green', alpha=0.7, linestyle='--')
    ungraded_quiz_performance.plot(kind='line', marker='o', ax=ax2, color='red', alpha=0.7, linestyle='--')

    ax1.set_title('Session Duration vs Quiz Performance')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Average Session Length (s)')
    ax2.set_ylabel('Quiz Performance (%)')

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # Set x-axis labels to be horizontal
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)

    plt.tight_layout(rect=[0, 0.01, 1, 0.95])
    plt.show()


# Plotting the metrics
plot_certificates_vs_session_length_and_completion_rates(certificates, average_session_length, completion_rates)
plot_session_duration_vs_quiz_performance(average_session_length, graded_quiz_performance, ungraded_quiz_performance)