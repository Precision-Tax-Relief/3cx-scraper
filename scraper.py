import csv
import os
import sys
from io import StringIO
from time import sleep
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR, encoding='utf-8', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.addHandler(logging.StreamHandler(sys.stdout))


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
        print(f'Navigating to Call Report page in Admin Console')
        self.driver.get(self.urls['call_reports'])

        # Wait for the page to be fully loaded
        WebDriverWait(self.driver, 30).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
        sleep(2)
        print('Page loaded.')

    ###############################
    # AUTHENTICATION
    ###############################
    def login(self, username, password):
        print('Logging in.')
        self.driver.get(self.urls['signin'])
        username_field = self.wait_for_element((By.ID, 'loginInput'))
        password_field = self.driver.find_element(By.ID, 'passwordInput')

        username_field.send_keys(username)
        password_field.send_keys(password)

        self.driver.find_element(By.ID, 'submitBtn').click()
        WebDriverWait(self.driver, 30).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
        print('Logged in.')


    ###############################
    # CALL REPORTING
    ###############################
    def get_call_reports_table(self) -> StringIO:
        print('Getting report from Call Report table.')

        # Wait for table to be present
        table = self.wait_for_element((By.XPATH, '//div[@id="scrollableList"]//table'), quit_on_fail=True)
        print('Got table')

        # Wait for rows to be loaded (wait for at least one row in tbody)
        self.wait_for_element((By.XPATH, '//div[@id="scrollableList"]//table//tbody/tr[1]'), timeout=30)
        print('Got first row, table is populated')

        # Get column names from thead
        thead = table.find_element(By.XPATH, './/thead')
        table_headers = thead.find_elements(By.XPATH, './/th')

        headers_text = []
        for header in table_headers[:-1]:  # Last column is the actions button
            headers_text.append(header.text.strip())

        print(f'Found {len(headers_text)} headers')
        print(', '.join(headers_text))

        # Create a CSV writer with StringIO to handle proper escaping
        output = StringIO()
        csv_writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Write headers to CSV
        csv_writer.writerow(headers_text)

        # Get tbody and its rows
        tbody = table.find_element(By.XPATH, './/tbody')

        # Add explicit wait for all rows to be loaded
        rows = WebDriverWait(self.driver, 30).until(
            lambda x: tbody.find_elements(By.XPATH, './/tr')
        )
        print(f'Found {len(rows)} rows')

        # Process each row
        for row in rows:
            cells = row.find_elements(By.XPATH, './/td')
            cells_text = []
            for cell in cells[:-1]:  # Skip the last cell (actions)
                cells_text.append(cell.text.strip())
            csv_writer.writerow(cells_text)
            print(cells_text)
        csv_text = output.getvalue()
        return csv_text



    ###############################
    # TESTING
    ###############################
    def take_screenshot(self, name):
        """
        Takes a screenshot and saves it to the screenshots directory
        """
        try:
            os.makedirs('screenshots', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'screenshots/{name}_{timestamp}.png'
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")


