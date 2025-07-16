import datetime
import json
import time

import pandas as pd
import csv
from itertools import zip_longest
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

course_data = []

def check_element(link_text):
    try:
        driver.find_element(By.LINK_TEXT, link_text)
    except NoSuchElementException:
        return False
    return True

def scrape_stat_values(ajax_wrapper):
    rows = ajax_wrapper.find_elements(By.CSS_SELECTOR, 'div.row')
    for row in rows:
        try:
            value_element = row.find_element(By.CLASS_NAME, 'col-xs-4')
            value_element = value_element.find_element(By.CSS_SELECTOR, 'data-selector')
            shadow_host1 = value_element.find_element(By.CLASS_NAME, 'absolute')
            shadow_root1 = driver.execute_script('return arguments[0].shadowRoot', shadow_host1)
            shadow_host2 = WebDriverWait(shadow_root1, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'count-up')))
            shadow_root2 = driver.execute_script('return arguments[0].shadowRoot', shadow_host2)
            value = shadow_root2.find_element(By.CSS_SELECTOR, '#counter').text
            header = row.find_element(By.CLASS_NAME, 'col-xs-8.text-right').text
            yield header, value
        except NoSuchElementException:
            pass


def scrape_kpi_values(driver, section_name, base_xpath, num_items):
    for i in range(1, num_items + 1):

        wrapper = driver.find_element(By.XPATH, f'{base_xpath}[{i}]')
        item = wrapper.find_element(By.CSS_SELECTOR, 'data-selector')
        item_host = item.find_element(By.CLASS_NAME , 'score-card')
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', item_host)
        item = shadow_root.find_element(By.CSS_SELECTOR, '#content-container')
        header = item.find_element(By.CSS_SELECTOR, '#name').text
        shadow_host1 = item.find_element(By.CSS_SELECTOR, 'counter-basic')

        if section_name == 'learning_items' and i in [5, 6]:
            value = shadow_host1.text
        else:
            shadow_root1 = driver.execute_script('return arguments[0].shadowRoot', shadow_host1)
            shadow_host2 = WebDriverWait(shadow_root1, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'count-up')))
            shadow_root2 = driver.execute_script('return arguments[0].shadowRoot', shadow_host2)
            value = shadow_root2.find_element(By.CSS_SELECTOR, '#counter').text
        yield header, value



def scrape_plot_values(ajax_wrapper):
    rows = ajax_wrapper.find_elements(By.CLASS_NAME, 'col-md-12')
    for row in rows:
        value_element = row.find_element(By.CSS_SELECTOR, 'data-filter')
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', value_element)
        filters = shadow_root.find_element(By.CSS_SELECTOR, '#filterBar')
        for i, filter in enumerate(filters.find_elements(By.CSS_SELECTOR, 'paper-button')):
            if i == 0:
                header = filter.text
                shadow_host1 =  value_element.find_element(By.CSS_SELECTOR, 'linechart-basic')
                shadow_root1 = driver.execute_script('return arguments[0].shadowRoot', shadow_host1)
                shadow_host2 = WebDriverWait(shadow_root1, 120).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#diagram')))
                plot = shadow_host2.find_element(By.CLASS_NAME, 'js-plotly-plot')
                value = driver.execute_script(f'return arguments[0].data;', plot)
                value = value[0]

                transformed_data = [{"x": date, "y": value} for date, value in
                                   zip(value["x"], value["y"])]
                driver.execute_script("arguments[0].click();", filter)
            else:
                driver.execute_script("arguments[0].click();", filter)
                header = filter.text
                shadow_host1 = value_element.find_element(By.CSS_SELECTOR, 'linechart-basic')
                shadow_root1 = driver.execute_script('return arguments[0].shadowRoot', shadow_host1)
                shadow_host2 = WebDriverWait(shadow_root1, 120).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#diagram')))
                plot = shadow_host2.find_element(By.CLASS_NAME, 'js-plotly-plot')
                value = driver.execute_script(f'return arguments[0].data;', plot)
                value = value[0]

                transformed_data = [{"x": date, "y": value} for date, value in
                                    zip(value["x"], value["y"])]
                driver.execute_script("arguments[0].click();", filter)

            yield header, transformed_data


def scrape_data(driver, wait, dict):
    with open('course_data.csv', 'w', newline='') as csvfile, open('course_data.json', 'w') as jsonfile:
        fieldnames = ['timestamp', 'code', 'name', 'status', 'start', 'end', 'section', 'header', 'value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        course_data = []
        for course, data in dict.items():
            try:
                stats = {}

                new_tab_url = data['link']
                driver.get(new_tab_url)

                try:
                    course_dates = wait.until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, 'enrollment-statistics__date-value')))
                    start_date = course_dates[2].text
                    end_date = course_dates[1].text
                except:
                    new_tab_url = data['link'] + f'/edit#formgroup-dates'
                    driver.get(new_tab_url)
                    start_date = wait.until(
                        EC.presence_of_element_located((By.ID, 'course_start_date'))).get_attribute("value")
                    end_date = wait.until(
                        EC.presence_of_element_located((By.ID, 'course_end_date'))).get_attribute("value")

                new_tab_url = data['link'] + f'/dashboard'
                driver.get(new_tab_url)
                # Get the height of the page
                height = driver.execute_script("return document.body.scrollHeight")

                # Scroll to the bottom of the page in 1 second
                driver.execute_script(
                    f"var interval = setInterval(function() {{ window.scrollBy(0, {height / 10}); }}, 100); setTimeout(function() {{ clearInterval(interval); }}, 1000);")

                # Wait for scrolling to finish
                time.sleep(1)

                # get the current timestamp
                timestamp = datetime.datetime.now().isoformat()

                # define the base xpaths for each section
                base_xpaths = [
                    ('plots', '/html/body/div[2]/div[2]/div[2]/div/div[5]/div/ajax-wrapper', 2),
                    ('stats', '/html/body/div[2]/div[2]/div[2]/div/div[3]/div/ajax-wrapper', 0),
                    ('learning_items', '/html/body/div[2]/div[2]/div[2]/div/div[4]/div/div[1]/ajax-wrapper', 6),
                    ('forum', '/html/body/div[2]/div[2]/div[2]/div/div[4]/div/ajax-wrapper[1]/div/div', 10),
                    ('badges', '/html/body/div[2]/div[2]/div[2]/div/div[4]/div/ajax-wrapper[2]/div/div', 3),
                    ('misc', '/html/body/div[2]/div[2]/div[2]/div/div[4]/div/div[2]/ajax-wrapper', 2)
                ]

                for section_name, base_xpath, num_items in base_xpaths:
                    if section_name == 'plots':
                        ajax_wrapper = driver.find_element(By.XPATH, base_xpath)
                        for header, value in scrape_plot_values(ajax_wrapper):
                            row = {
                                'timestamp': timestamp,
                                'code': course,
                                'name': data['name'],
                                'status': data['status'],
                                'start': start_date,
                                'end': end_date,
                                'section': section_name,
                                'header': header,
                                'value': value,
                            }
                            writer.writerow(row)
                            course_data.append(row)

                    elif section_name == 'stats':
                        ajax_wrappers = driver.find_elements(By.XPATH, base_xpath)
                        for ajax_wrapper in ajax_wrappers:
                            for header, value in scrape_stat_values(ajax_wrapper):
                                print(f'{section_name}: {header} = {value}')
                                row = {
                                    'timestamp': timestamp,
                                    'code': course,
                                    'name': data['name'],
                                    'status': data['status'],
                                    'start': start_date,
                                    'end': end_date,
                                    'section': section_name,
                                    'header': header,
                                    'value': value,
                                }
                                writer.writerow(row)
                                course_data.append(row)
                    else:
                        for header, value in scrape_kpi_values(driver, section_name, base_xpath, num_items):
                            print(f'{section_name}: {header} = {value}')
                            row = {
                                'timestamp': timestamp,
                                'code': course,
                                'name': data['name'],
                                'status': data['status'],
                                'start': start_date,
                                'end': end_date,
                                'section': section_name,
                                'header': header,
                                'value': value,
                            }
                            writer.writerow(row)
                            course_data.append(row)

                json.dump(course_data, jsonfile)
            except Exception as e:
                print(f"Error occurred while processing course: {course}. Error: {e}")

if __name__ == '__main__':

    driver = webdriver.Chrome()

    wait = WebDriverWait(driver, 10)

    website_url = 'https://open.hpi.de/sessions/new'
    driver.get(website_url)

    # Login credentials for the website
    username = 'siddhant.gadamsetti@hpi.de'
    password = 'Manasadevi@0211'

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

    driver.execute_script("window.open('about:blank','secondtab');")

    driver.switch_to.window("secondtab")

    prep_courses = {}
    arch_courses = {}
    acti_courses = {}

    for i in range(1,8):
        new_tab_url = f'https://open.hpi.de/admin/courses?page={i}'
        driver.get(new_tab_url)

        course_list = wait.until(
                EC.presence_of_element_located((By.ID, 'admin-courses__content')))

        max_courses = len(course_list.find_elements(By.CSS_SELECTOR, 'tr'))

        for i in range(1, max_courses):
            course = course_list.find_element(By.CSS_SELECTOR, f"#admin-courses__content > tbody > tr:nth-child({i}) > td:nth-child({2})").text
            code = course_list.find_element(By.CSS_SELECTOR, f"#admin-courses__content > tbody > tr:nth-child({i}) > td:nth-child({1})").text
            link =  course_list.find_element(By.CSS_SELECTOR,
                                       f"#admin-courses__content > tbody > tr:nth-child({i}) > td:nth-child({2})").find_element(By.CSS_SELECTOR,'a').get_attribute("href")
            status = course_list.find_element(By.CSS_SELECTOR,
                                       f"#admin-courses__content > tbody > tr:nth-child({i}) > td:nth-child({3})").text
            if status == "archive":
                arch_courses[code] = {'name':course,'link':link, 'status':"archive"}
            elif status == "active":
                acti_courses[code] = {'name':course,'link':link, 'status':"active"}
            elif status == "preparation":
                prep_courses[code] = {'name': course, 'link': link, 'status':"preparation"}

    arch_courses_df = pd.DataFrame(arch_courses).T
    acti_courses_df = pd.DataFrame(acti_courses).T
    prep_courses_df = pd.DataFrame(prep_courses).T

    arch_courses_df.to_csv('archived_courses.csv')
    acti_courses_df.to_csv('active_courses.csv')
    prep_courses_df.to_csv('upcoming_courses.csv')

    driver.execute_script("window.open('about:blank','thirdtab');")
    driver.switch_to.window("thirdtab")

    scrape_data(driver, wait, acti_courses)

    course_data_df = pd.DataFrame(course_data)
    course_data_df.to_csv('course_data.csv', index=False)
