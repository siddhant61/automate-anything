import pandas as pd

# Define file paths
files = [
    'C:/Users/siddh/Desktop/openHPI/reports/Survey/pythonjunior-schule2023.csv',
    'C:/Users/siddh/Desktop/openHPI/reports/Survey/pythonjunior-schule2024.csv',
    'C:/Users/siddh/Desktop/openHPI/reports/Survey/javaeinstieg-schule2023.csv',
    'C:/Users/siddh/Desktop/openHPI/reports/Survey/javaeinstieg-schule2024.csv',
    'C:/Users/siddh/Desktop/openHPI/reports/Survey/pythonjunior2023-1.csv',
    'C:/Users/siddh/Desktop/openHPI/reports/Survey/pythonjunior2023-2.csv'
]


# Function to collect teacher user data for a specific file
def collect_teacher_data(file, option_columns):
    df = pd.read_csv(file)
    teacher_data = pd.DataFrame()

    # Define the columns to keep in the final output
    base_columns = ['user_id', 'user_name', 'email', 'accessed_at', 'submitted_at', 'submit_duration', 'points']

    for option in option_columns:
        if option in df.columns:
            teacher_df = df[df[option] == '1']
            if not teacher_df.empty:
                # Select the base columns and the relevant teacher-indicating column
                relevant_columns = base_columns + [option]
                teacher_data = pd.concat([teacher_data, teacher_df[relevant_columns]])
        else:
            print(f"Warning: Column '{option}' not found in {file}")

    return teacher_data


# Define file paths and relevant columns for each report
files_and_columns = {
    "C:/Users/siddh/Desktop/openHPI/reports/Survey/pythonjunior2023-1.csv": ['lehrkraft'],
    "C:/Users/siddh/Desktop/openHPI/reports/Survey/pythonjunior2023-2.csv": ['lehrkraft'],
    "C:/Users/siddh/Desktop/openHPI/reports/Survey/pythonjunior-schule2023.csv": [
        'ich_bin_lehrkraft_und_betreue_meine_schler_innen_in_diesem_kurs',
        'ich_bin_lehrkraft_und_mchte_mir_den_kurs_anschauen'
    ],
    "C:/Users/siddh/Desktop/openHPI/reports/Survey/pythonjunior-schule2024.csv": [
        'ich_bin_lehrkraft_und_betreue_meine_schler_innen_in_diesem_kurs',
        'ich_bin_lehrkraft_und_mchte_mir_den_kurs_anschauen',
        'lehrkraft'
    ],
    "C:/Users/siddh/Desktop/openHPI/reports/Survey/javaeinstieg-schule2023.csv": [
        'ich_bin_lehrkraft_und_betreue_meine_schler_innen_in_diesem_kurs',
        'ich_bin_lehrkraft_und_mchte_mir_den_kurs_anschauen'
    ],
    "C:/Users/siddh/Desktop/openHPI/reports/Survey/javaeinstieg-schule2024.csv": [
        'ich_bin_lehrkraft_und_betreue_meine_schler_innen_in_diesem_kurs',
        'ich_bin_lehrkraft_und_mchte_mir_den_kurs_anschauen',
        'lehrkraft'
    ]
}

# Initialize an empty DataFrame to collect all teacher data from all reports
all_teacher_data = pd.DataFrame()

# Process each file and collect teacher data
for file, columns in files_and_columns.items():
    print(f"Processing file: {file}")
    teacher_data = collect_teacher_data(file, columns)
    all_teacher_data = pd.concat([all_teacher_data, teacher_data])

# Remove duplicate entries based on user_id
all_teacher_data.drop_duplicates(subset=['user_id'], inplace=True)

# Save the collected teacher data to a CSV file
output_file = "C:/Users/siddh/Desktop/openHPI/reports/Survey/teacher_user_data.csv"
all_teacher_data.to_csv(output_file, index=False)

# Print the DataFrame to inspect the results
print(all_teacher_data)

print(f"Teacher user data has been saved to {output_file}")