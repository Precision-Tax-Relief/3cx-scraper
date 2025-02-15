import os
from datetime import date, timedelta, datetime
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import logging

logger = logging.getLogger()


class Scraper:
    def __init__(self,
                 driver,
                 wait_time=15,
                 ):
        self.driver = driver
        self.wait_time = wait_time
        self.urls = {
            'signin': 'https://precisiontaxrelief.3cx.us:5001/#/login',
            'call_reports': 'https://precisiontaxrelief.3cx.us:5001/#/office/reports/call-reports'
        }

    ###############################
    # UTILITY FUNCTIONS
    ###############################
    def wait_for_element(self, query: tuple, timeout: int = 15, quit_on_fail: bool = True):
        # timeout = timeout or self.wait_time
        timeout = 30
        try:
            i = WebDriverWait(self.driver, timeout, poll_frequency=.25).until(
                EC.presence_of_element_located(query)
            )
            return i
        except Exception as e:
            if quit_on_fail:
                self.driver.quit()
                raise e
            else:
                print(f'Element not found for query: {query}')
                return None

    def wait_for_element_to_be_clickable(self, element, timeout=None):
        timeout = timeout or self.wait_time
        print('Waiting for element to be clickable.')
        try:
            i = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(element)
            )
            return i
        except Exception as e:
            self.driver.quit()
            raise e

    ###############################
    # NAVIGATION
    ###############################
    def navigate_to_call_report_admin(self):
        logger.info(f'Navigating to Call Report page in Admin Console')
        self.driver.get(self.urls['call_reports'])


    ###############################
    # AUTHENTICATION
    ###############################
    def login(self, username, password):
        logger.info('Logging in.')
        self.driver.get(self.urls['signin'])
        username_field = self.wait_for_element((By.ID, 'loginInput'))
        password_field = self.driver.find_element(By.ID, 'passwordInput')

        username_field.send_keys(username)
        password_field.send_keys(password)

        self.driver.find_element(By.ID, 'submitBtn').click()
        sleep(2)


    ###############################
    # CALL REPORTING
    ###############################
    def get_call_reports_table(self):
        print('Getting report from Call Report table.')
        table = self.wait_for_element((By.XPATH, '//div[@id="scrollableList"]//table'), quit_on_fail=True)
        print('Got table')

        # Get column names from thead
        thead = table.find_element(By.XPATH, './/thead')
        table_headers = thead.find_elements(By.XPATH, './/th')

        headers_text = []
        for header in table_headers[:-1]:  # Last column is the actions button
            headers_text.append(header.text.strip())

        print(f'Found {len(headers_text)} headers')
        print(', '.join(headers_text))

        # Start building CSV text with headers
        csv_text = f'{",".join(headers_text)}\n'

        # Get tbody and its rows
        tbody = table.find_element(By.XPATH, './/tbody')
        rows = tbody.find_elements(By.XPATH, './/tr')

        # Process each row
        for row in rows:
            cells = row.find_elements(By.XPATH, './/td')
            cells_text = []
            for cell in cells[:-1]:  # Skip the last cell (actions)
                cells_text.append(cell.text.strip())
            if cells_text:  # Only add non-empty rows
                csv_text += f'{",".join(cells_text)}\n'

        return csv_text