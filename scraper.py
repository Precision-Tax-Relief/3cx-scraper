import os
import re
import sys
import pandas as pd
from datetime import datetime, date
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    encoding='utf-8',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# logger.addHandler(logging.StreamHandler(sys.stdout))

class Scraper:
    def __init__(self,
                 driver,
                 wait_time=15,
                 DEBUG=False
                 ):
        self.driver = driver
        self.wait_time = wait_time
        self.DEBUG = DEBUG
        self.urls = {
            'signin': 'https://geo3-core1.intermaxnetworks.com/portal/',
            'call_reports': 'https://geo3-core1.intermaxnetworks.com/portal/callhistory',
            'call_reports_index': 'https://geo3-core1.intermaxnetworks.com/portal/callhistory/index/page:'
        }
        logger.info(f'{self.DEBUG = }')

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
                logger.warn(f'Element not found for query: {query}')
                return None

    def wait_for_element_to_be_clickable(self, element, timeout=None):
        timeout = timeout or self.wait_time
        logger.info('Waiting for element to be clickable.')
        try:
            i = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(element)
            )
            return i
        except Exception as e:
            self.driver.quit()
            raise e

    def wait_for_document_ready(self):
        # Wait for the page to be fully loaded
        WebDriverWait(self.driver, 30).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )

    ###############################
    # NAVIGATION
    ###############################
    def navigate_to_call_report_admin(self):
        logger.info(f'Navigating to Call Report page in Admin Console')
        self.driver.get(self.urls['call_reports'])

        self.wait_for_document_ready()
        if self.DEBUG:
            self.take_screenshot('document-ready-after-navigate-to-call-report-admin')
        logger.info('call report page loaded completely')

    def navigate_to_pagination_page(self, page_number):
        logger.info(f'Navigating to pagination page {page_number}')
        self.driver.get(self.urls['call_reports_index'] + str(page_number))
        self.wait_for_document_ready()
        if self.DEBUG:
            self.take_screenshot(f'page-{page_number}')
        logger.info(f'Navigated to pagination page {page_number}')


    ###############################
    # AUTHENTICATION
    ###############################
    def login(self, username, password):
        logger.info('Logging in.')
        self.driver.get(self.urls['signin'])
        username_field = self.wait_for_element((By.ID, 'LoginUsername'))
        password_field = self.driver.find_element(By.ID, 'LoginPassword')

        username_field.send_keys(username)
        password_field.send_keys(password)

        self.driver.find_element(By.XPATH, '//input[@type="submit"]').click()
        self.wait_for_document_ready()
        if self.DEBUG:
            self.take_screenshot('document-ready-after-login')

    ###############################
    # CALL REPORTING
    ###############################
    def check_if_report_is_empty(self):
        logger.info('Checking if report is empty.')
        if self.DEBUG:
            self.take_screenshot('before-check-if-report-is-empty')
        try:
            self.driver.find_element(By.XPATH, '//h3[text()="No calls have been found."]')
            logger.info('Report is empty')
            if self.DEBUG:
                self.take_screenshot('report-is-empty')
            return True
        except:
            return False


    def wait_for_recording_lookups(self, expected_rows):
        """
        Wait for all recording lookups to complete by monitoring console logs.
        expected_rows: number of rows in the current table
        """
        logger.info(f"Waiting for recording lookups to complete for {expected_rows} rows")

        def check_lookup_complete():
            # Get browser console logs
            logs = self.driver.get_log('browser')
            if not logs:
                return False

            # Look for the last status message
            for log in reversed(logs):
                message = log.get('message', '')
                if 'recording lookup status=' in message:
                    current, total = message.split('=')[1].strip().split('/')
                    # Check if we've reached the last row
                    if int(current) >= expected_rows:
                        return True
            return False

        # Wait up to 30 seconds for lookups to complete
        try:
            WebDriverWait(self.driver, 30, poll_frequency=0.5).until(
                lambda _: check_lookup_complete()
            )
            logger.info("Recording lookups completed")
        except Exception as e:
            logger.warning(f"Timeout waiting for recording lookups to complete: {str(e)}")

    def get_call_reports_table(self, date: date):
        logger.info('Getting report from Call Report table.')

        # Wait for table to be present
        table = self.wait_for_element((By.XPATH, '//table[@id="call-history-table"]'), quit_on_fail=True)

        # Get column names from thead
        thead = table.find_element(By.XPATH, './/thead')
        table_headers = thead.find_elements(By.XPATH, './/th')

        headers_text = []
        for header in table_headers[:-1]:  # Last column is the actions button
            headers_text.append(header.text.strip().lower().replace(' ', '_'))
        headers_text = headers_text + ['download_url', 'id']


        # Get tbody and its rows
        tbody = table.find_element(By.XPATH, './/tbody')
        rows = tbody.find_elements(By.XPATH, './/tr[@recindex]')
        row_count = len(rows)

        # Wait for all recording ajax lookups to complete
        self.wait_for_recording_lookups(row_count)

        data = []
        # Process each row
        for row in rows:
            cells = row.find_elements(By.XPATH, './/td')
            cells_text = []
            for cell in cells[:-1]:  # Skip the last cell (actions)
                cells_text.append(cell.text.strip())

            transcription_link = row.find_element(By.XPATH, './/td[@class="action-buttons"]/a[1]')
            transcription_link = transcription_link.get_attribute('href')
            cells_text.append(transcription_link or '')

            # Get ID from notes link
            notes_link = row.find_element(By.XPATH, './/td[@class="action-buttons"]/a[@class="helpsy reports"]')
            notes_link = notes_link.get_attribute('href')
            id = notes_link.split('/')[-1]
            cells_text.append(id)

            data.append(cells_text)

        df = pd.DataFrame(data, columns=headers_text)


        # Remove the 'qos' columns
        df = df.loc[:, ~df.columns.str.contains('qos', case=False)]

        # Format the 'date' column as a datetime object
        def parse_date(date_str):
            try:
                # Remove the 'th', 'st', 'nd', 'rd' from the day
                date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

                # Try parsing with year first
                try:
                    date_obj = datetime.strptime(date_str, '%b %d %Y %I:%M %p')
                except ValueError:
                    # If that fails, try without year and add current year
                    date_obj = datetime.strptime(date_str, '%b %d %I:%M %p').replace(year=date.today().year)

                return date_obj.isoformat()
            except ValueError as e:
                logger.warning(f'Failed to parse date: {date_str}')
                raise f'Failed to parse date: {date_str} - {str(e)}'
                return None

        df['date'] = df['date'].apply(parse_date)

        return df

    def set_table_size_100(self):
        logger.info('Setting table size to 100')
        # Check if table size is already set to 100
        parent_li = self.driver.find_element(By.XPATH, '//a[@id="LinkPager100"]/ancestor::li')
        if 'active' in parent_li.get_attribute('class'):
            logger.info('Table size is already set to 100')
            return

        # Scroll to the bottom of the page
        logger.info('Scrolling to the bottom of the page')
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        if self.DEBUG:
            self.take_screenshot('pager100-before-click')
        # Set table size
        pager100 = self.driver.find_element(By.XPATH, '//a[@id="LinkPager100"]')
        pager100.click()

        # Check again after load
        parent_li = self.driver.find_element(By.XPATH, '//a[@id="LinkPager100"]/ancestor::li')
        if self.DEBUG:
            self.take_screenshot('pager100-after-click')
        if 'active' in parent_li.get_attribute('class'):
            logger.info('Table size is set to 100')
            return
        else:
            logger.error('Failed to set table size to 100')
            raise Exception('Failed to set table size to 100')

    def set_date_filter(self, day):
        date_string = date.strftime(day, '%m/%d/%Y')

        filters_btn = self.wait_for_element((By.XPATH, '//a[@id="LinkFilters"]'))
        filters_btn.click()

        from_field = self.wait_for_element((By.ID, 'from-0'))
        to_field = self.wait_for_element((By.ID, 'to-0'))

        from_field.clear()
        to_field.clear()

        from_field.send_keys(date_string)
        to_field.send_keys(date_string)

        if self.DEBUG:
            self.take_screenshot('date-filter-set')

        submit_btn = self.wait_for_element((By.XPATH, '//form[@id="callhistoryFiltersForm"]//input[@type="submit"]'))
        submit_btn.click()
        self.wait_for_document_ready()

        if self.DEBUG:
            self.take_screenshot('date-filter-submitted')

    def get_pagination_count(self):
        pagination_links = self.driver.find_elements(By.XPATH, '//div[@class="pagination pull-left"]//a')
        max_page = 1

        # Iterate through the links and extract page numbers
        for link in pagination_links:
            href = link.get_attribute('href')
            if href:  # Ensure href is not None
                # Extract page number using regex
                match = re.search(r'page:(\d+)', href)
                if match:
                    page_number = int(match.group(1))
                    max_page = max(max_page, page_number)

        return max_page


    ###############################
    # TESTING
    ###############################
    def take_screenshot(self, name):
        """
        Takes a screenshot and saves it to the screenshots directory
        """
        try:
            os.makedirs('screenshots', exist_ok=True)
            screenshot_dir = os.path.join(os.getcwd(), 'screenshots')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(screenshot_dir, f'{timestamp}_{name}.png')
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")


    def clear_screenshot_directory(self):
        """
        Clears all files in the screenshots directory.
        """
        screenshot_dir = 'screenshots'
        try:
            if os.path.exists(screenshot_dir):
                # Iterate and remove each file in the directory
                for file_name in os.listdir(screenshot_dir):
                    file_path = os.path.join(screenshot_dir, file_name)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.info(f"Removed screenshot: {file_path}")
                logger.info("Screenshot directory cleared successfully.")
            else:
                logger.warning("Screenshot directory does not exist. Nothing to clear.")
        except Exception as e:
            logger.error(f"Failed to clear screenshot directory: {str(e)}")
