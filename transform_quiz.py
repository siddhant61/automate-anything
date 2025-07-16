import pandas as pd

def transform_data(file_path):
    # Load the data
    data = pd.read_csv(file_path)

    # Identify the question columns and their options
    columns = data.columns.tolist()
    questions_corrected = {}
    current_question = None
    for col in columns[5:]:  # Skip the first five columns
        if data[col].isna().all():  # New question column if all values are NaN
            if current_question:
                questions_corrected[current_question['name']] = current_question['options']
            current_question = {'name': col, 'options': []}
        else:
            if current_question:
                current_question['options'].append(col)
    if current_question:
        questions_corrected[current_question['name']] = current_question['options']

    # Transform the dataset
    data_transformed = data.iloc[:, :5].copy()  # Copy the first five columns
    for question, options in questions_corrected.items():
        data_transformed[question] = pd.NA  # Initialize the question column
        for option in options:
            data_transformed.loc[data[option] == '1', question] = option
        data.drop(columns=options, inplace=True)  # Remove the original option columns

    return data_transformed

# Path to the CSV file
file_path = 'D:/quiz reports/end/pythonjunior-schule2023_course_end.csv'

# Apply the transformation
transformed_data = transform_data(file_path)
print(transformed_data.head())

transformed_data.to_csv('D:/quiz reports/transformed_reports/pythonjunior-schule2023_course_end.csv', index=False)


start = pd.read_csv('D:/quiz reports/end/pythonjunior-schule2023_course_start.csv')
end = pd.read_csv('D:/quiz reports/end/pythonjunior-schule2023_course_end.csv')
combined = pd.merge(start, end, on="user_pseudo_id")