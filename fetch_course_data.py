import pandas as pd
import csv
from itertools import zip_longest
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

course_data = {}

course_code = input("Enter course code: ")

driver = webdriver.Chrome()

wait = WebDriverWait(driver, 10)

website_url = 'https://open.hpi.de/sessions/new'
driver.get(website_url)

# Login credentials for the website
username = 'siddhant.gadamsetti@hpi.de'
password = 'Manasadevi@0211'

# hpi_login = wait.until(
#     EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div/div[2]/ul/li[1]/a')))
#
# hpi_login.click()

# Find the username and password input fields and enter the login credentials
username_field = wait.until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="login_email"]')))
username_field.send_keys(username)

password_field = wait.until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="login_password"]')))
password_field.send_keys(password)

# Click the login button
login_button = wait.until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="login-form"]/div[1]/form/div[3]')))
login_button.click()

stats = {}

new_tab_url = 'https://open.hpi.de/courses/' + f'{course_code}'
driver.get(new_tab_url)

try:
    course_dates = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'enrollment-statistics__date-value')))
    start_date = course_dates[2].text
    end_date = course_dates[1].text
except:
    new_tab_url = 'https://open.hpi.de/courses/' + f'{course_code}' + f'/edit#formgroup-dates'
    driver.get(new_tab_url)
    start_date = wait.until(
        EC.presence_of_element_located((By.ID, 'course_start_date'))).get_attribute("value")
    end_date = wait.until(
        EC.presence_of_element_located((By.ID, 'course_end_date'))).get_attribute("value")

new_tab_url = 'https://open.hpi.de/courses/' + f'{course_code}' + f'/dashboard'
driver.get(new_tab_url)

sleep(2)

stats_table = wait.until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[2]/div/div[3]/div/ajax-wrapper')))

cols = WebDriverWait(stats_table, 10).until(
EC.visibility_of_any_elements_located((By.CLASS_NAME, 'course-dashboard-section')))

for col in cols:
    rows = col.find_elements(By.CLASS_NAME, 'row.kpis__row')
    for i in range(0, len(rows)):
        value = rows[i].find_element(By.CLASS_NAME, 'col-xs-4')
        value = value.find_element(By.CSS_SELECTOR, 'data-selector')
        shadow_host1 = value.find_element(By.CLASS_NAME, 'absolute')
        shadow_root1 = driver.execute_script('return arguments[0].shadowRoot', shadow_host1)
        shadow_host2 = WebDriverWait(shadow_root1, 120).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'count-up')))
        shadow_root2 = driver.execute_script('return arguments[0].shadowRoot', shadow_host2)
        content = shadow_root2.find_element(By.CSS_SELECTOR, '#counter').text

        header = rows[i].find_element(By.CLASS_NAME, 'col-xs-8.text-right').text

        stats[header] = content

print(stats)



