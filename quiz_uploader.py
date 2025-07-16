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

if __name__ == '__main__':

    page = input("Enter page name: ")

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

    url = f'https://open.hpi.de/pages/{page}'

    driver.get(url)

    col = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[2]')

    editors = col.find_elements(By.CLASS_NAME, 'text-truncate')

    editors[0].click()

    input_field= driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div/form/div[4]/div/div/div/div[1]/textarea')

    input_field.clear()

    with open('C:/Users/siddh/Documents/Work/faq.txt', 'r', encoding='utf-8') as file:
        data = file.read()

    input_field.send_keys(data)

    driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div/form/div[5]/div/input').click()

    print("Page updated.")