import datetime
import json
import time
import pandas as pd
import csv
from itertools import zip_longest
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep


def safe_wait_for_element(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        print(f"Couldn't find element with {by} = {value} after waiting for {timeout} seconds.")
        return None



if __name__ == '__main__':

    course_structure = {}

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    wait = WebDriverWait(driver, 10)

    website_url = 'https://open.hpi.de/sessions/new'
    driver.get(website_url)

    # Click on HPI Identity
    hpi_login = wait.until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div/div[2]/ul/li[1]/a')))
    hpi_login.click()

    # Login credentials for the website
    username = 'siddhant.gadamsetti'
    password = 'Manasadevi@2321'

    # Find the username and password input fields and enter the login credentials
    username_field = wait.until(
        EC.presence_of_element_located((By.NAME, 'login')))
    username_field.send_keys(username)

    password_field = wait.until(
        EC.presence_of_element_located((By.NAME, 'password')))
    password_field.send_keys(password)

    # Click the login button
    login_button = wait.until(
        EC.presence_of_element_located((By.XPATH, '//button[@type="submit"]')))
    login_button.click()

    new_tab_url = f'https://open.hpi.de/courses/qc-optimization2023/'
    driver.get(new_tab_url)

    enroll = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="qc-optimization2023"]/div/div[1]/div[2]/div[4]/div/a')))
    if enroll:
        enroll.click()
        print("Enrolled to the course")

    driver.execute_script("window.open('about:blank','secondtab');")

    driver.switch_to.window("secondtab")

    new_tab_url = f'https://open.hpi.de/courses/qc-optimization2023/overview'
    driver.get(new_tab_url)

    overview_content = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, 'course-area-main')))

    rows = overview_content.find_elements(By.CLASS_NAME, 'course-area-main__title')

    for i, row in enumerate(rows):
        if i != 0:
            driver.switch_to.window("secondtab")

        title = row.text
        content_desc = row.find_element(By.XPATH, f'/html/body/div[2]/div[2]/div[2]/div[1]/div[2]/div/div/div[{i+1}]/div[1]').text
        time.sleep(0.5)
        content_elem = row.find_element(By.XPATH, f'/html/body/div[2]/div[2]/div[2]/div[1]/div[2]/div/div/div[{i+1}]/div[2]')
        subsec_links = content_elem.find_elements(By.CLASS_NAME, 'item-status')

        lines = content_elem.text.split('\n')

        subsections = lines[::2]
        types = lines[1::2]
        links = []


        for link in subsec_links:
            links.append(link.get_attribute('href'))

        for j in range(len(links)):
            if i == 0:
                driver.execute_script("window.open('about:blank','thirdtab');")

            driver.switch_to.window("thirdtab")

            driver.get(links[j])

            if types[j] == "Text":
                # Find the section by xpath
                section = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[1]/div[2]/div')))

                # Get the data from the section
                data = section.text

            elif types[j] == 'Survey':
                # Find the section by xpath
                section = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[1]/div[2]/div/div[1]')))
                #
                # # Find the form by its id
                # form = section.find_element(By.ID,'quiz_form')
                #
                # # Find the input elements within the form
                # inputs = form.find_elements(By.TAG_NAME, 'input')
                #
                # # Now get the data from each input
                # for input in inputs:
                #     name = input.get_attribute('name')
                #     value = input.get_attribute('value')
                #     print(f'name: {name}, value: {value}')

                # Get the data from the section
                data = section.text

            elif types[j] == 'Self-test':
                # Find the section by xpath
                section = wait.until(
                EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]')))
                #
                # # Find the form by its id
                # form = section.find_element(By.ID,'quiz_form')
                #
                # # Find the input elements within the form
                # inputs = form.find_elements(By.TAG_NAME, 'input')
                #
                # # Now get the data from each input
                # for input in inputs:
                #     name = input.get_attribute('name')
                #     value = input.get_attribute('value')
                #     print(f'name: {name}, value: {value}')

                # Get the data from the section
                data = section.text


            elif types[j] == 'Video':
                # Find the section by xpath
                player = driver.find_element(By.CLASS_NAME, 'video-player')
                lecture = player.find_element(By.XPATH, '//*[@id="player-container"]/div/xm-player/xm-vimeo[1]')
                try:
                    ppt = player.find_element(By.XPATH, '//*[@id="player-container"]/div/xm-player/xm-vimeo[2]')
                    # Get the data from the section
                    data = "Lecture stream: https://player.vimeo.com/video/" + lecture.get_attribute('src') \
                           + ", PPT stream: https://player.vimeo.com/video/" + ppt.get_attribute('src')
                except:
                    # Get the data from the section
                    data = "Lecture stream: https://player.vimeo.com/video/" + lecture.get_attribute('src')



            else:
                data = None



            course_structure[f'section-{i + 1}.{j + 1}'] = {'section': title, 'description': content_desc,
                                                           'subsection': subsections[j], 'type': types[j],
                                                           'link': links[j], 'data':data}


    # Save to file
    with open('qc-optimization2023.json', 'w') as f:
        json.dump(course_structure, f, indent=4)