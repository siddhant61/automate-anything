import csv

import pandas as pd
import matplotlib.pyplot as plt

# Load the data from each file
java_2024 = pd.read_csv('D:/quiz reports/javaeinstieg-schule2024.csv')
python_junior_2023 = pd.read_csv('D:/quiz reports/pythonjunior_schule2023.csv')
python_junior_2023_1 = pd.read_csv('D:/quiz reports/pythonjunior2023_1.csv')
python_junior_2024 = pd.read_csv('D:/quiz reports/pythonjunior-schule2024.csv')
java_2023 = pd.read_csv('D:/quiz reports/javaeinstieg_schule2023.csv')

# Define age and student-related columns specifically
age_columns_below_20 = {
    'java_2024': ['jnger_als_14_jahre', '14_15_jahre', '16_17_jahre', '18_19_jahre'],
    'python_junior_2023': ['jnger_als_10_jahre', '10_bis_12_jahre', '13_bis_15_jahre', '16_bis_18_jahre', '19_bis_20_jahre'],
    'python_junior_2023_1': ['jnger_als_12_jahre', '12_bis_13_jahre', '14_bis_15_jahre', '16_bis_17_jahre', '18_bis_19_jahre'],
    'python_junior_2024': ['jnger_als_14_jahre', '14_15_jahre', '16_17_jahre', '18_19_jahre'],
    'java_2023': ['jnger_als_20_jahre']
}

age_columns_above_20 = {
    'java_2024': ['20_29_jahre', '30_39_jahre', '40_49_jahre', '50_59_jahre', '60_69_jahre', '70_jahre'],
    'python_junior_2023': ['21_bis_29_jahre', '30_bis_39_jahre', '40_bis_49_jahre', '50_bis_59_jahre', '60_bis_69_jahre', 'lter_als_70_jahre'],
    'python_junior_2023_1': ['20_bis_29_jahre', '30_bis_39_jahre', '40_bis_49_jahre', '50_bis_59_jahre', '60_jahre_und_lter'],
    'python_junior_2024': ['20_29_jahre', '30_39_jahre', '40_49_jahre', '50_59_jahre', '60_69_jahre', '70_jahre'],
    'java_2023': ['20_29_jahre', '30_39_jahre', '40_49_jahre', '50_59_jahre', '60_69_jahre', '70_jahre_oder_lter']
}

student_columns = {
    'java_2024': ['ich_bin_schlerin', 'ich_bin_lehrkraft_und_betreue_meine_schlerinnen_in_diesem_kurs'],
    'python_junior_2023': ['ich_bin_schler_in_und_besuche_diesen_kurs_im_rahmen_des_unterrichts'],
    'python_junior_2023_1': ['schlerin'],
    'python_junior_2024': ['ich_bin_schlerin', 'ich_bin_lehrkraft_und_betreue_meine_schlerinnen_in_diesem_kurs'],
    'java_2023': ['ich_bin_schler_in_und_besuche_diesen_kurs_im_rahmen_des_unterrichts']
}

# Function to filter users below and above 20 years
def filter_users(df, below_20_cols, above_20_cols, student_cols):
    # Convert all relevant columns to numeric, handling non-numeric as zero
    df[below_20_cols + above_20_cols + student_cols] = df[below_20_cols + above_20_cols + student_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Create filters based on age
    below_20_filter = df[below_20_cols].sum(axis=1) > 0
    above_20_filter = df[above_20_cols].sum(axis=1) > 0

    # Adjust the below 20 filter to include students
    student_filter = df[student_cols].sum(axis=1) > 0
    below_20_filter |= student_filter

    return df[below_20_filter], df[above_20_filter]

# Apply filtering to each course
users_below_20 = {}
users_above_20 = {}
for course in age_columns_below_20.keys():
    df = eval(course.replace(' ', '_').lower())  # This matches the dataframe variable names
    below_20, above_20 = filter_users(df, age_columns_below_20[course], age_columns_above_20[course], student_columns[course])
    users_below_20[course] = below_20
    users_above_20[course] = above_20


# Visualization for age comparison across courses
def plot_comparison():
    courses = list(users_below_20.keys())
    below_20_counts = [len(data) for data in users_below_20.values()]
    above_20_counts = [len(data) for data in users_above_20.values()]
    total_counts = [below + above for below, above in zip(below_20_counts, above_20_counts)]

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35
    indices = range(len(courses))

    bars_below_20 = ax.bar(indices, below_20_counts, bar_width, label='Below 20 Years', color='skyblue')
    bars_above_20 = ax.bar([i + bar_width for i in indices], above_20_counts, bar_width, label='20 Years and Above', color='coral')

    ax.set_xlabel('Courses')
    ax.set_ylabel('Number of Users')
    ax.set_title('Comparison of Users Below and Above 20 Years Across Courses')
    ax.set_xticks([i + bar_width / 2 for i in indices])
    ax.set_xticklabels(courses)
    ax.legend()

    # Adding percentage labels to the bars
    for i, (bar_below_20, bar_above_20) in enumerate(zip(bars_below_20, bars_above_20)):
        below_20_count = below_20_counts[i]
        above_20_count = above_20_counts[i]
        total_count = total_counts[i]

        # Annotate percentage for below 20
        below_20_percentage = below_20_count / total_count * 100
        ax.annotate(f'{below_20_percentage:.1f}%', xy=(bar_below_20.get_x() + bar_below_20.get_width() / 2, bar_below_20.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

        # Annotate percentage for above 20
        above_20_percentage = above_20_count / total_count * 100
        ax.annotate(f'{above_20_percentage:.1f}%', xy=(bar_above_20.get_x() + bar_above_20.get_width() / 2, bar_above_20.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()



plot_comparison()


