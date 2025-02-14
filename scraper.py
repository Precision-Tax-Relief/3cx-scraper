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
                 date_time_format='%b %-d, %Y  %-I:%M %p',
                 date_format='%m/%d/%Y',
                 download_dir='/Downloads/',
                 export_period=11,
                 destination_dir=None,
                 locations=None,
                 ):
        self.driver = driver
        self.wait_time = wait_time
        self.date_time_format = date_time_format
        self.date_format = date_format
        self.export_period = timedelta(days=export_period)
        self.download_dir = download_dir
        self.destination_dir = destination_dir
        self.urls = {
            'signin': 'https://precisiontaxrelief.3cx.us:5001/#/login',
            'call_history': 'https://precisiontaxrelief.3cx.us:5001/#/call_history'
        }

    ###############################
    # UTILITY FUNCTIONS
    ###############################
    def wait_for_element(self, query: tuple, timeout: int = None, quit_on_fail: bool = True):
        timeout = timeout or self.wait_time
        try:
            i = WebDriverWait(self.driver, timeout, poll_frequency=.05).until(
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

    def wait_for_loader(self, query, short_wait=None, long_wait=None):
        short_wait = short_wait or self.wait_time / 2
        long_wait = long_wait or self.wait_time
        try:
            WebDriverWait(self.driver, short_wait, poll_frequency=0.1).until(
                EC.presence_of_element_located(query),
            )
            WebDriverWait(self.driver, long_wait).until_not(
                EC.presence_of_element_located(query)
            )
        except Exception as e:
            print('Loader not found')
            raise Exception(e)

    def change_export_view(self, value):
        try:
            view_select = self.wait_for_element((By.ID, 'ctl00_ctl00_content_content_ddlViewing'))
            view_select.click()
            view_select.find_element(By.XPATH, f'//option[@value="{value}"]').click()
            self.wait_for_element((By.XPATH, f'//option[@value="{value}" and @selected="selected"]'))
        except Exception as e:
            print(e)
            raise Exception('Error changing view')

    def get_time_string(self, time_object):
        return time_object.strftime(self.date_time_format).replace('AM', 'am').replace('PM', 'pm')

    def get_date_string(self, time_object):
        return time_object.strftime(self.date_format)

    def get_file_date_string(self, time):
        return time.strftime('%Y-%m-%d')

    def search_for_export_button(self, time):
        time_string = self.get_time_string(time)
        print(f'Searching for export button with time {time_string}')
        if self.wait_for_element((By.XPATH, f"//a[string()='{time_string}']"), quit_on_fail=False):
            print(f'Found export at {time_string}')
            return time_string
        else:
            print(f'Export not found at {time_string}')
            return None

    def get_download_dir_filecount(self):
        files = [file for file in os.listdir(self.download_dir) if 'crdownload' not in file.lower() and 'Chrome' not in file]
        return len(files)

    def wait_until_filecount_reached(self, count: int, timeout: int = None):
        print(f'Waiting for file count to reach {count}')
        timeout = timeout or self.wait_time
        for i in range(timeout):
            if self.get_download_dir_filecount() >= count:
                return True
            sleep(1)
        return False

    def move_file(self, type, location=None, start_date=None, end_date=None):
        # Skip if no destination dir
        if self.destination_dir is None:
            return
        # Validate type
        print(f'Moving {type} file')
        file_types = ['Customer', 'Appointment', 'Order']
        if type not in file_types:
            raise Exception(f'File type must be one of {file_types}')
        # Create subdirectory if it doesn't exist
        sub_dir = os.path.join(self.destination_dir, type)
        if not os.path.exists(sub_dir):
            os.mkdir(sub_dir)
        if location is not None:
            sub_dir = os.path.join(sub_dir, location)
            if not os.path.exists(sub_dir):
                os.mkdir(sub_dir)
        # Set destination file name
        dest_file_name = type
        if start_date:
            dest_file_name += f' {self.get_file_date_string(start_date).replace("/", "_")}'
            if end_date:
                dest_file_name += f'-{self.get_file_date_string(end_date).replace("/", "_")}'
        # Get file name
        file_name = [file for file in os.listdir(self.download_dir) if type in file]
        if len(file_name) == 0:
            raise Exception(f'No file found for type {type}')
        elif len(file_name) > 1:
            raise Exception(f'Multiple files found for type {type}')
        # Move file
        src = os.path.join(self.download_dir, file_name[0])
        dest = os.path.join(sub_dir, f'{dest_file_name}.csv')
        print(f'Moving file {src} to {dest}')
        os.rename(src, dest)

    ###############################
    # NAVIGATION
    ###############################
    def navigate_to_treatmnent_detail(self, treatment_id):
        print(f'Navigating to treatment detail page. {treatment_id = }')
        self.driver.get(self.urls['treatment_detail'].format(treatment_id))

    def navigate_to_appointments_page(self):
        print('Navigating to appointments page.')
        self.driver.get(self.urls['appointments'])

    def navigate_to_orders_page(self):
        print('Navigating to orders page.')
        self.driver.get(self.urls['orders'])

    def navigate_to_locations_page(self):
        print('Navigating to locations page.')
        self.driver.get(self.urls['locations'])

    def navigate_to_customers_page(self):
        print('Navigating to customers page.')
        self.driver.get(self.urls['customers'])

    def select_location(self, location_code):
        self.navigate_to_locations_page()
        print('Selecting location.')
        location_select = self.wait_for_element((By.XPATH, f"//a[@href='Impersonate.aspx?SpaID={location_code}']"))
        location_select.click()
        sleep(1)

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

    ###############################
    # CUSTOMERS
    ###############################
    def customers_start_export(self, view_id=57514):
        print('Starting customers export.')
        self.change_export_view(view_id)
        # export button
        self.driver.find_element(By.ID, 'ctl00_ctl00_content_content_btnExport').click()
        start_time = datetime.now(self.timezone) + timedelta(seconds=15)  # Booker seems to round up sometimes. This hits the correct time the first time more often
        print(f'Export started at {self.get_time_string(start_time)}')
        sleep(5)
        ok_button = self.wait_for_element((By.XPATH, '//input[@value="Ok" and @class="xSubmitPrimary"]'),
                                          quit_on_fail=False)
        if ok_button:
            print('Export started, clicking ok.')
            ok_button.click()
            sleep(2)
        else:
            print('Export started, no ok button found.')
        return start_time

    def customers_download_export(self, time):
        time_string = self.get_time_string(time)
        print(f'Looking for export started near {time_string}')

        export_time = self.search_for_export_button(time)
        # Check for race condition
        if export_time is None:
            export_time = self.search_for_export_button(time + timedelta(minutes=1))
        if export_time is None:
            export_time = self.search_for_export_button(time - timedelta(minutes=1))

        if export_time is None:
            raise Exception('Export not found')


        button_text = export_time
        print('Waiting for export to finish')
        sleep(3)
        self.driver.refresh()
        sleep(1)
        export_download_button = None
        for i in range(0, 10):
            export_download_button = self.wait_for_element(
                (By.XPATH, f"//a[string()='{button_text}' and @title='download .csv file']"),
                timeout=self.wait_time,
                quit_on_fail=False
            )
            if export_download_button is not None:
                break
            else:
                self.driver.refresh()
                print('Export not found. Refreshing page.')

        if export_download_button is None:
            raise Exception('Customer Export Button not found to be clickable')
        export_download_button.click()
        print('Customer export download started')

    def customer_flow(self, view_id=57514):
        filecount = self.get_download_dir_filecount()

        self.select_location(self.locations['ll']['id'])
        self.navigate_to_customers_page()
        export_time = self.customers_start_export(view_id)
        self.customers_download_export(export_time)
        sleep(1)
        print('Waiting for download to finish')
        if not self.wait_until_filecount_reached(filecount + 1):
            raise Exception('Customer download did not finish in a timely manner')
        print('Customer download finished')
        self.move_file('Customer', start_date=export_time)

    def customer_added_today_flow(self):
        self.select_location(self.locations['ll']['id'])
        self.navigate_to_customers_page()
        self.change_export_view(59300)
        export_time = datetime.now(self.timezone)

        select_more_rows_xpath = "//select[@name='ctl00$ctl00$content$content$grdSearchResults$ctl14$ctl02']"
        select_more_rows = self.wait_for_element((By.XPATH, select_more_rows_xpath), quit_on_fail=False)
        if select_more_rows is not None:
            select_more_rows.click()
            select_more_rows.find_element(By.XPATH, ".//option[@value='100']").click()
            sleep(3)

        table_xpath = "//table[@class='grdSearchResults']/tbody"
        table = self.wait_for_element((By.XPATH, table_xpath))
        rows = table.find_elements(By.XPATH, "./tr[@align='left']")
        print(f'Found {len(rows)} rows')


        file_path = os.path.join(self.download_dir, f'Customer.csv')
        with open(file_path, 'w') as f:
            for row in rows:
                cells = row.find_elements(By.XPATH, ".//th | .//td")
                for cell in cells:
                    f.write(f'"{cell.text}"')
                    f.write(',')
                f.write('\n')
        with open(file_path, 'r') as f:
            print(f.read())
        self.move_file('Customer', start_date=export_time)

    def customer_added_last_year_flow(self):
        self.customer_flow(59301)

    def customer_added_last_week_flow(self):
        self.customer_flow(59303)

    def customer_create_select_location(self):
        self.select_location(self.locations['ll']['id'])

    def customer_create_flow(self, customer_data: dict):
        self.customer_create_select_location()
        self.navigate_to_customers_page()

        import time
        from functools import wraps

        def retry(max_attempts, delay_seconds):
            def decorator(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    attempts = 0
                    while attempts < max_attempts:
                        try:
                            return func(*args, **kwargs)
                        except Exception as e:
                            attempts += 1
                            print(f"Attempt {attempts}/{max_attempts} failed: {e}")
                            time.sleep(delay_seconds)
                    return func(*args, **kwargs)

                return wrapper

            return decorator

        @retry(max_attempts=3, delay_seconds=0.1)
        def create_customer():
            print('Navigating to create customer page.')
            self.driver.get(self.urls['customers_create'])
            print('Filling out customer form.')
            first_name = customer_data.get('first_name', None) or customer_data.get('firstName', None)
            if not first_name:
                raise Exception('First name required')
            first_name_field = self.wait_for_element(
                (By.ID, 'ctl00_ctl00_content_content_ucDynamicForm_ctl01_ctl00_txtValue'))
            first_name_field.send_keys(first_name)
            last_name = customer_data.get('last_name', None) or customer_data.get('lastName', None)
            if not last_name:
                raise Exception('Last name required')
            last_name_field = self.wait_for_element(
                (By.ID, 'ctl00_ctl00_content_content_ucDynamicForm_ctl04_ctl00_txtValue'))
            last_name_field.send_keys(last_name)
            email = customer_data.get('email', None)
            if email:
                email_field = self.wait_for_element(
                    (By.ID, 'ctl00_ctl00_content_content_ucDynamicForm_ctl05_ctl00_txtValue'))
                email_field.click()
                email_field.send_keys(email)
                first_name_field.click()
            phone = customer_data.get('phone', '')
            if phone:
                phone = phone.replace('+1', '')
                sleep(.5)
                from selenium.webdriver.common.keys import Keys
                phone_field = self.wait_for_element(
                    (By.ID, 'ctl00_ctl00_content_content_ucDynamicForm_ctl11_ctl00_ctlPhone_txtMaskedNumber'))
                phone_field.click()
                for i in range(14):
                    phone_field.send_keys(Keys.BACKSPACE)
                phone_field.send_keys(phone)
                sleep(.5)
            print('Saving customer.')
            save_button = self.wait_for_element(
                (By.ID, 'ctl00_ctl00_content_content_btnSubmit'))
            save_button.click()
            print('Customer submitted.')
            sleep(1)
            detail_tabs = self.wait_for_element(
                (By.XPATH, "//a[@title='Details']"),
                quit_on_fail=False,
                timeout=self.wait_time // 2
            )
            if detail_tabs is not None:
                detail_tabs.click()
                print('Navigating to details tab.')
                guid = self.wait_for_element(
                    (By.ID, "ctl00_ctl00_content_content_ucDetails_ucDynamicForm_ctl29_ctl00_lblValueEdit"))
                guid = str(guid.text).replace('{', '').replace('}', '')
                print(f'Customer guid: {guid}')
                return guid
            else:
                customer_exists_error = self.wait_for_element(
                    (By.XPATH, "//span[@class='xError' and contains(text(), 'Another customer exists')]"))
                if customer_exists_error is not None:
                    print('Customer already exists.')
                    if email:
                        print('Searching for customer by email.')
                        guid = self.customer_get_guid_by_email(email)
                        if guid:
                            return guid
                        print('Customer not found by email.')
                    elif phone:
                        print('Searching for customer by phone.')
                        guid = self.customer_get_guid_by_phone(phone)
                        if guid:
                            return guid
                        print('Customer not found by phone.')
                    raise Exception('Customer already exists but could not be found by email or phone.')
                raise Exception('Unexpected error creating customer')

        return create_customer()

    def customer_get_guid_by_email(self, email: str):
        self.customer_create_select_location()
        self.navigate_to_customers_page()

        email_field = self.wait_for_element((By.ID, 'ctl00_ctl00_content_content_txtEmail'))
        email_field.send_keys(email)
        search_button = self.wait_for_element(
            (By.ID, 'ctl00_ctl00_content_content_btnSearch'))
        search_button.click()
        sleep(1)

        table_xpath = "//table[@class='grdSearchResults']/tbody"
        table = self.wait_for_element((By.XPATH, table_xpath))
        rows = table.find_elements(By.TAG_NAME, 'tr')[1:]
        if len(rows) == 0:
            print(f'No customers found with email {email}')
            return None
        elif len(rows) > 1:
            print(f'WARNING: Multiple customers found with email {email}')
        review_button = rows[0].find_element(By.XPATH, ".//a[@title='Review']")
        review_button.click()
        sleep(1)
        detail_tabs = self.wait_for_element(
            (By.XPATH, "//a[@title='Details']"))
        detail_tabs.click()
        print('Navigating to details tab.')
        guid = self.wait_for_element(
            (By.ID, "ctl00_ctl00_content_content_ucDetails_ucDynamicForm_ctl29_ctl00_lblValueEdit"))
        guid = str(guid.text).replace('{', '').replace('}', '')
        print(f'Customer guid: {guid}')
        return guid

    def customer_get_guid_by_phone(self, phone: str):
        from selenium.webdriver import Keys
        self.customer_create_select_location()
        self.navigate_to_customers_page()

        phone_field = self.wait_for_element((By.ID, 'ctl00_ctl00_content_content_ctlPhoneNumberStrict_txtMaskedNumber'))
        for i in range(14):
            phone_field.send_keys(Keys.BACKSPACE)
        phone_field.send_keys(phone)
        search_button = self.wait_for_element(
            (By.ID, 'ctl00_ctl00_content_content_btnSearch'))
        search_button.click()
        sleep(1)

        table_xpath = "//table[@class='grdSearchResults']/tbody"
        table = self.wait_for_element((By.XPATH, table_xpath))
        rows = table.find_elements(By.TAG_NAME, 'tr')[1:]
        if len(rows) == 0:
            print(f'No customers found with phone {phone}')
            return None
        elif len(rows) > 1:
            print(f'WARNING: Multiple customers found with phone {phone}')
        review_button = rows[0].find_element(By.XPATH, ".//a[@title='Review']")
        review_button.click()
        sleep(1)
        detail_tabs = self.wait_for_element(
            (By.XPATH, "//a[@title='Details']"))
        detail_tabs.click()
        print('Navigating to details tab.')
        guid = self.wait_for_element(
            (By.ID, "ctl00_ctl00_content_content_ucDetails_ucDynamicForm_ctl29_ctl00_lblValueEdit"))
        guid = str(guid.text).replace('{', '').replace('}', '')
        print(f'Customer guid: {guid}')
        return guid




    ###############################
    # APPOINTMENTS
    ###############################
    def appointments_export_chunked(self, start_date, end_date):
        start_string = self.get_date_string(start_date)
        end_string = self.get_date_string(end_date)
        print(f'Exporting appointments from {start_string} to {end_string}')
        self.wait_for_element((By.ID, 'ctl00_ctl00_content_content_txtDate'))
        self.driver.execute_script(f"$('#ctl00_ctl00_content_content_txtDate').val('{start_string} - {end_string}');")
        sleep(0.1)
        self.driver.execute_script("""
            let event = new Event('change');
            document.querySelector('#ctl00_ctl00_content_content_txtDate').dispatchEvent(event);
            """)

        self.wait_for_loader((By.XPATH, '//div[@class="reports-overlay-words"]'))
        self.driver.find_element(By.ID, 'ctl00_ctl00_content_content_btnExport').click()

    def appointments_export(self, location):
        current_time = self.start_date
        while current_time < self.end_date + self.export_period:
            sleep(60)
            file_count = self.get_download_dir_filecount()
            query_end = current_time + self.export_period - timedelta(days=1)
            self.appointments_export_chunked(current_time, query_end)
            # Wait for file download to show up in directory
            if not self.wait_until_filecount_reached(file_count + 1):
                raise Exception('Appointment download did not finish in a timely manner')
            self.move_file('Appointment', location=location, start_date=current_time, end_date=query_end)
            current_time += self.export_period

    def appointments_flow(self, location, date_type='date_on'):
        self.select_location(location['id'])
        self.navigate_to_appointments_page()

        if date_type == 'date_created':
            value = 'ApptCreatedOn'
            try:
                view_select = self.wait_for_element((By.ID, 'ctl00_ctl00_content_content_ddlDateType'))
                view_select.click()
                view_select.find_element(By.XPATH, f'//option[@value="{value}"]').click()
                self.wait_for_element((By.XPATH, f'//option[@value="{value}" and @selected="selected"]'))
            except Exception as e:
                print(e)
                raise Exception('Error changing view')

        self.change_export_view(location['appointments_view_id'])
        self.appointments_export(location=location['id'])

    def appointment_map_booking_numbers_to_orders(self, location, booking_numbers: list):
        self.select_location(location['id'])

        # booking_order_map = {}
        for booking_number in booking_numbers:
            print(f'Getting order number for booking number {booking_number}')
            self.navigate_to_appointments_page()
            booking_number_field = self.wait_for_element((By.ID, 'ctl00_ctl00_content_content_txtBookingNumber'))
            booking_number_field.send_keys(str(booking_number))
            search_button = self.wait_for_element(
                (By.XPATH, "//div[@id='ctl00_ctl00_content_content_pnlLeft']//input[@id='ctl00_ctl00_content_content_btnSearch']"))
            search_button.click()
            sleep(.25)
            view_button = self.wait_for_element(
                (By.XPATH, "//div[@id='ctl00_ctl00_content_content_upnlSearchResults']//table[@id='ctl00_ctl00_content_content_grdSearchResults']/tbody/tr[@class='xTr'][1]//a[@title='View' or @title='Review']"),
                quit_on_fail=False
            )
            if view_button is None:
                print(f'Appointment not found for booking number {booking_number}')
                continue
            view_button.click()
            order_xpath = '//*[@id="ctl00_ctl00_content_content_ucViewAppointment_ucAppointmentHeaderBlock_lnkViewOrder" or @id="ctl00_ctl00_content_content_ucViewGroupAppointment_ucGroupHeaderBlock_lnkViewOrder" or @id="ctl00_ctl00_content_content_ucViewGroupAppointment_ucGroupHeaderBlock_rptOrders_ctl01_lnkViewOrder"]'
            order_number_element = self.wait_for_element((By.XPATH, order_xpath), quit_on_fail=True)
            order_number = order_number_element.text
            # booking_order_map[booking_number] = order_number_element.text
            print(f'Order number for booking number {booking_number}: {order_number}')
            yield booking_number, order_number

        return

    ###############################
    # ORDERS
    ###############################
    def orders_export_chunked(self, start_time: date, end_time: date):
        start_string = self.get_date_string(start_time)
        end_string = self.get_date_string(end_time)
        print(f'Exporting orders from {start_string} to {end_string}')
        self.wait_for_element((By.ID, 'ctl00_ctl00_content_content_txtDateCreated'))
        self.driver.execute_script(f"$('#ctl00_ctl00_content_content_txtDateCreated').val('{start_string} - {end_string}');")
        sleep(0.1)
        self.driver.execute_script("""
            let event = new Event('change');
            document.querySelector('#ctl00_ctl00_content_content_txtDateCreated').dispatchEvent(event);
            """)
        sleep(0.2)
        # wait_for_loader(driver, (By.XPATH, '//div[@class="reports-overlay-words"]'))
        self.wait_for_element((By.ID, 'ctl00_ctl00_content_content_btnExport')).click()

    def orders_export(self, location=None):
        current_time = self.start_date
        while current_time < self.end_date + self.export_period:
            file_count = self.get_download_dir_filecount()
            query_end = current_time + self.export_period - timedelta(days=1)
            self.orders_export_chunked(current_time, query_end)
            # Wait for file download to show up in directory
            if not self.wait_until_filecount_reached(file_count + 1, self.wait_time*2):
                raise Exception('Order download did not finish in a timely manner')
            self.move_file('Order', location=location, start_date=current_time, end_date=query_end)
            current_time += self.export_period

    def orders_flow(self, location):
        self.select_location(location['id'])
        self.navigate_to_orders_page()
        self.change_export_view(location['orders_view_id'])
        self.orders_export(location['id'])
