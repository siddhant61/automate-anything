import pandas as pd
import csv
from itertools import zip_longest
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

def check_element(link_text):
    try:
        driver.find_element(By.LINK_TEXT, link_text)
    except NoSuchElementException:
        return False
    return True

# Replace with the path to your webdriver
driver = webdriver.Chrome()

website_url = 'https://open.hpi.de/sessions/new'
driver.get(website_url)

# Login credentials for the website
username = 'siddhant.gadamsetti'
password = 'Manasadevi@0211'

hpi_login = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div/div[2]/ul/li[1]/a')))

hpi_login.click()

# Find the username and password input fields and enter the login credentials
username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'login')))
username_field.send_keys(username)

password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'password')))
password_field.send_keys(password)

# Click the login button
login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/main/form/p[1]/button')))
login_button.click()

driver.execute_script("window.open('about:blank','secondtab');")

driver.switch_to.window("secondtab")

new_tab_url = 'https://open.hpi.de/users'
driver.get(new_tab_url)

# CSV file containing email addresses
csv_file_path = 'C:/Users/siddh/Documents/Work/emails.csv'
emails = pd.read_csv(csv_file_path)

enrolled_emails = []
unregistered_emails = []
all_emails = []

# Loop through the email addresses and enter each one into the input field, then click the button
for email in emails['email']:
    usersearch_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'user_filter_query')))

    usersearch_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[1]/div[1]/div/form/input[2]')))
    usersearch_field.clear()
    usersearch_field.send_keys(email)
    usersearch_btn.click()

    if check_element('Details'):
        userdetails_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Details')))
        userdetails_btn.click()

        masq_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/a[2]')))

        masq_btn.click()

        driver.execute_script("window.open('about:blank','thirdtab');")

        driver.switch_to.window("thirdtab")

        new_tab_url = 'https://open.hpi.de/courses/hpi-emoocs2023'
        driver.get(new_tab_url)

        sleep(2)

        if check_element('Enter course'):
            print(f"{email} is already enrolled.")
        else:
            enroll_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[2]/div/div[1]/div[2]/div[4]/div/a')))
            enroll_btn.click()
            sleep(1)

        demasq = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, 'DEMASQ')))

        demasq.click()

        enrolled_emails.append(email)


        driver.switch_to.window("secondtab")

        driver.refresh()

        new_tab_url = 'https://open.hpi.de/users'

        driver.get(new_tab_url)

    else:
        unregistered_emails.append(email)
        print(f"{email} not registered")

driver.quit()

all_emails.append(enrolled_emails, unregistered_emails)

with open("out_emails.csv","w+") as f:
    writer = csv.writer(f)
    for values in zip_longest(*all_emails):
        writer.writerow(values)
