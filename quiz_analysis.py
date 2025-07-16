import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
file_path = 'D:/python_quiz_report.csv'
data = pd.read_csv(file_path)

# Define age group columns and labels
age_columns = ['jnger_als_14_jahre', '14_15_jahre', '16_17_jahre', '18_19_jahre', '20_29_jahre']
age_groups = ['<14', '14-15', '16-17', '18-19', '20-29']

# Create a unified age group column based on existing age group columns
data['age_group'] = None
for col, group in zip(age_columns, age_groups):
    data.loc[data[col] == '1', 'age_group'] = group

# Filter the dataset for individuals up to 29 years old
youth_data = data[data['age_group'].isin(age_groups)]

# Function to convert columns to numeric and sum up for visualization
def prepare_data(columns, labels):
    data_series = pd.Series(index=labels, dtype=int)
    for col, label in zip(columns, labels):
        youth_data[col] = pd.to_numeric(youth_data[col], errors='coerce')
        data_series[label] = youth_data[col].sum()
    return data_series

# Age Distribution Visualization
plt.figure(figsize=(10, 6))
youth_data['age_group'].value_counts().sort_index().plot(kind='bar', color='skyblue')
plt.title('Age Distribution of Respondents up to 29 Years Old')
plt.xlabel('Age Group')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# Gender Distribution Visualization
gender_columns = ['weiblich', 'mnnlich', 'divers__anderes_geschlecht']
gender_labels = ['Female', 'Male', 'Diverse']
gender_data = prepare_data(gender_columns, gender_labels)
plt.figure(figsize=(8, 5))
gender_data.plot(kind='bar', color='skyblue')
plt.title('Gender Distribution of Respondents up to 29 Years Old')
plt.xlabel('Gender')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# Group Affiliation Visualization:
group_columns = ['ich_bin_schlerin_und_besuche_diesen_kurs_im_rahmen_des_unterrichts',
                 'ich_bin_schlerin_und_besuche_den_kurs_in_meiner_freizeit',
                 'ich_bin_lehrkraft_und_betreue_meine_schlerinnen_in_diesem_kurs',
                 'ich_bin_lehrkraft_und_mchte_mir_den_kurs_anschauen',
                 'keiner_dieser_gruppen',
                 'ich_bin_elternteil_und_begleite_mein_kind_in_diesem_kurs']
group_labels = ['Student (In Class)', 'Student (Free Time)', 'Teacher (With Students)',
                'Teacher (Exploring)', 'None of the Above', 'Parent Supporting']
group_data = prepare_data(group_columns, group_labels)
plt.figure(figsize=(12, 7))
group_data.plot(kind='bar', color='skyblue')
plt.title('Group Affiliation of Respondents up to 29 Years Old')
plt.xlabel('Group')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# Visualizing non-student group affiliation
non_student_columns = ['selbstndig', 'rentnerin__pensionrin', 'angestellter__beamtein',
                       'studentin', 'ohne_beschftigungsverhltnis']
non_student_labels = ['Self-employed', 'Retiree', 'Employee', 'University Student', 'Unemployed']

# Initialize non-student group affiliation data
non_student_data = pd.Series(index=non_student_labels, dtype=int)

# Ensure the non-student group columns are treated as numeric and fill non-student group affiliation data
for col, label in zip(non_student_columns, non_student_labels):
    youth_data[col] = pd.to_numeric(youth_data[col], errors='coerce')
    non_student_data[label] = youth_data[col].sum()

# Plotting non-student group affiliation
plt.figure(figsize=(10, 6))
non_student_data.plot(kind='bar', color='skyblue')
plt.title('Non-Student Group Affiliation of Respondents up to 29 Years Old')
plt.xlabel('Group')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# Visualizing course discovery methods
discovery_columns = ['durch_die_schule_lehrerin_mitschlerin', 'suchmaschine_z_b_google',
                     'mooc_aggregator_z_b_mooc_list_class_central_moo_chub', 'soziale_medien_linked_in_facebook_twitter',
                     'zeitung_auch_online', 'freundinnen_bekannte_kolleginnen',
                     'auf_der_plattform_open_hpi_gefunden', 'newsletter__e_mail_von_open_hpi', 'andere']
discovery_labels = ['School', 'Search Engine', 'MOOC Aggregator', 'Social Media',
                    'Newspaper', 'Friends/Family', 'Platform openHPI', 'Newsletter', 'Other']

# Initialize course discovery data
discovery_data = pd.Series(index=discovery_labels, dtype=int)

# Ensure the discovery columns are treated as numeric and fill course discovery data
for col, label in zip(discovery_columns, discovery_labels):
    youth_data[col] = pd.to_numeric(youth_data[col], errors='coerce')
    discovery_data[label] = youth_data[col].sum()

# Plotting course discovery methods
plt.figure(figsize=(12, 7))
discovery_data.plot(kind='bar', color='skyblue')
plt.title('Course Discovery Methods of Respondents up to 29 Years Old')
plt.xlabel('Method')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# Visualizing reasons for taking the course
reason_columns = ['ich_will_das_abschlusszeugnis_erhalten', 'ich_will_alle_themen_sehen_das_zeugnis_ist_mir_aber_nicht_wichtig',
                  'ich_interessiere_mich_nur_fr_ausgewhlte_inhalte', 'ich_will_mich_nur_umsehen']
reason_labels = ['For Certification', 'See All Content (No Cert)', 'Selected Content Only', 'Just Browsing']

# Initialize reasons for taking the course data
reason_data = pd.Series(index=reason_labels, dtype=int)

# Ensure the reason columns are treated as numeric and fill reasons for taking the course data
for col, label in zip(reason_columns, reason_labels):
    youth_data[col] = pd.to_numeric(youth_data[col], errors='coerce')
    reason_data[label] = youth_data[col].sum()

# Plotting reasons for taking the course
plt.figure(figsize=(10, 6))
reason_data.plot(kind='bar', color='skyblue')
plt.title('Reasons for Taking the Course Among Respondents up to 29 Years Old')
plt.xlabel('Reason')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# Visualizing types of content of interest
content_columns = ['die_videos_die_mir_neues_wissen_vermitteln',
                   'die_selbsttests_mit_denen_ich_mein_wissen_prfen_und_mich_auf_die_bewerteten_hausaufgaben_vorbereiten_kann',
                   'die_programmieraufgaben_bei_denen_ich_das_wissen_praktisch_anwenden_und_vertiefen_kann',
                   'das_forum_in_dem_ich_mich_mit_anderen_austauschen_kann']
content_labels = ['Videos', 'Self-tests', 'Programming Tasks', 'Forum']

# Initialize types of content of interest data
content_data = pd.Series(index=content_labels, dtype=int)

# Ensure the content columns are treated as numeric and fill types of content data
for col, label in zip(content_columns, content_labels):
    youth_data[col] = pd.to_numeric(youth_data[col], errors='coerce')
    content_data[label] = youth_data[col].sum()

# Plotting types of content of interest
plt.figure(figsize=(10, 6))
content_data.plot(kind='bar', color='skyblue')
plt.title('Types of Content of Interest Among Respondents up to 29 Years Old')
plt.xlabel('Type of Content')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# Visualizing the hours spent on the course per week
time_columns = ['weniger_als_2_stunden_pro_woche', '2_bis_3_stunden_pro_woche', '4_bis_5_stunden_pro_woche', '6_bis_7_stunden_pro_woche',
                   '8_bis_9_stunden_pro_woche', '10_bis_11_stunden_pro_woche', '12_und_mehr_stunden_pro_woche']
time_labels = ['Up to 2 Hours ', '2 to 3 Hours', '4 to 5 Hours', '6 to 7 Hours', '8 to 9 Hours', '10 to 11 Hours', '12+ Hours']

# Initialize types of content of interest data
time_data = pd.Series(index=time_labels, dtype=int)

# Ensure the content columns are treated as numeric and fill types of content data
for col, label in zip(time_columns, time_labels):
    youth_data[col] = pd.to_numeric(youth_data[col], errors='coerce')
    time_data[label] = youth_data[col].sum()

# Plotting types of content of interest
plt.figure(figsize=(10, 6))
time_data.plot(kind='bar', color='skyblue')
plt.title('Hours Spent on the Course per Week Among Respondents up to 29 Years Old')
plt.xlabel('Time Spent')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# Visualizing prior knowledge of programming among respondents
code_columns = ['nein_ich_habe_noch_nie_etwas_programmiert', 'ja_ich_habe_schon_im_unterricht_programmiert',
                'ja_ich_programmiere_ab_und_zu_in_meiner_freizeit', 'ja_ich_programmiere_hufig']
code_labels = ['No prior knowlegde', 'Codes in class', 'Codes in leisure time', 'Codes frequently']

# Initialize types of content of interest data
code_data = pd.Series(index=code_labels, dtype=int)

# Ensure the content columns are treated as numeric and fill types of content data
for col, label in zip(code_columns, code_labels):
    youth_data[col] = pd.to_numeric(youth_data[col], errors='coerce')
    code_data[label] = youth_data[col].sum()

# Plotting types of content of interest
plt.figure(figsize=(10, 6))
code_data.plot(kind='bar', color='skyblue')
plt.title('Prior Knowledge of Programming among Among Respondents up to 29 Years Old')
plt.xlabel('Level of Prior Programming knowledge')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# Visualizing prior programming courses  among respondents
codecourse_columns = ['ja_genau_einen_auf_open_hpi', 'ja_mehrere_auf_open_hpi', 'ja_auf_einer_anderen_plattform_online',
                'ja_in_prsenz_zb_in_der_schule_universitt_aus__oder_weiterbildung_','nein_noch_gar_nicht']
codecourse_labels = ['One course on openHPI', 'Many courses on openHPI', 'On other Online Platforms', 'At School/Uni', 'No course at all']

# Initialize types of content of interest data
codecourse_data = pd.Series(index=codecourse_labels, dtype=int)

# Ensure the content columns are treated as numeric and fill types of content data
for col, label in zip(codecourse_columns, codecourse_labels):
    youth_data[col] = pd.to_numeric(youth_data[col], errors='coerce')
    codecourse_data[label] = youth_data[col].sum()

# Plotting types of content of interest
plt.figure(figsize=(10, 6))
codecourse_data.plot(kind='bar', color='skyblue')
plt.title('Prior Programming Courses Among Respondents up to 29 Years Old')
plt.xlabel('Prior Programming Courses')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# Visualizing the number of respondents with prior knowledge of Java
javacourse_columns = ['nein_ich_habe_noch_nie_etwas_mit_python_gemacht', 'ja_ich_habe_bereits_code_in_python_gesehen_aber_noch_nichts_selbst_programmiert',
                      'ja_ich_habe_bereits_erste_kleine_programme_in_python_geschrieben', 'ja_ich_habe_schon_viel_mit_python_gearbeitet_und_kann_auch_grere_programme_entwickeln',
                      'ja_ich_nutze_python_fast_tglich']
javacourse_labels = ['Never tried anythin in Python', 'Have seen Python code,\n never tried coding', 'Have written small codes in Python',
                     'Used to coding in Python,\n can write large codes', 'Use Python daily']

# Initialize types of content of interest data
javacourse_data = pd.Series(index=javacourse_labels, dtype=int)

# Ensure the content columns are treated as numeric and fill types of content data
for col, label in zip(javacourse_columns, javacourse_labels):
    youth_data[col] = pd.to_numeric(youth_data[col], errors='coerce')
    javacourse_data[label] = youth_data[col].sum()

# Plotting types of content of interest
plt.figure(figsize=(10, 6))
javacourse_data.plot(kind='bar', color='skyblue')
plt.title('Prior Knowledge of Python Among Respondents up to 29 Years Old')
plt.xlabel('Prior Knowledge of Python')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# Visualizing the number of respondents with prior usage of CodeOcean
codeocean_columns = ['nein', 'ja_ich_habe_bereits_ein_bisschen_erfahrung_mit_code_ocean', 'ja_ich_habe_bereits_viel_erfahrung_mit_code_ocean']
codeocean_labels = ['Never used CodeOcean', 'Some experience with CodeOcean', 'A lot of experience with CodeOcean']

# Initialize types of content of interest data
codeocean_data = pd.Series(index=codeocean_labels, dtype=int)

# Ensure the content columns are treated as numeric and fill types of content data
for col, label in zip(codeocean_columns, codeocean_labels):
    youth_data[col] = pd.to_numeric(youth_data[col], errors='coerce')
    codeocean_data[label] = youth_data[col].sum()

# Plotting types of content of interest
plt.figure(figsize=(10, 6))
codeocean_data.plot(kind='bar', color='skyblue')
plt.title('Prior Knowledge of CodeOcean Among Respondents up to 29 Years Old')
plt.xlabel('Prior Knowledge of CodeOcean')
plt.ylabel('Number of Respondents')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


