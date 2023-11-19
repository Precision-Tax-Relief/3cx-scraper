import os
from datetime import datetime
from invalid_file_handler import InvalidFileHandler
import pandas as pd

DATE_FORMAT = '%b %d, %Y'
DATETIME_FORMAT = '%b %-d, %Y  %-I:%M %p'


class BookerParser:
    def __init__(self, directory):
        self.directory = directory
        self.skip_invalid_move = True
        try:
            self.invalid_file_handler = InvalidFileHandler()
        except Exception as e:
            print('Could not initialize InvalidFileHandler')
            print(e)
            self.invalid_file_handler = None

        subdirectories = os.listdir(self.directory)
        categories = ['Appointments', 'Customers', 'Orders']
        self.category_directories = [c for c in subdirectories if c in categories]
        self.datetime_parser = lambda x: datetime.strptime(x, DATETIME_FORMAT.replace('-', '')).isoformat()
        self.date_parser = lambda x: datetime.strptime(x, '%b %d, %Y').isoformat()
        self.appointment_headers = {
            'Booking Number': 'booking_number',
            'Date Created': 'date_created',
            'Status': 'status',
            'Type': 'type',
            'Origin': 'origin',
            'Payment Method': 'payment_method',
            'Payment Special': 'payment_special',
            'Created By': 'created_by',
            'Pre-book / Rebook': 'pre_book_rebook',
            'Start Date/Time': 'start_date_time',
            'End Date/Time': 'end_date_time',
        }
        self.appointment_treatment_headers = {
            'Treatment Name': 'treatment_name',
            'Appointment On': 'appointment_on',
            'Category': 'category',
            'Subcategory': 'subcategory',
            'Staff Name': 'staff_name',
            'Room': 'room',
            'Duration': 'duration',
            'Price': 'price',
            'Staff Requested': 'staff_requested',
            'Tax': 'tax',
            'Total': 'total'
        }

        self.appointment_customer_headers = {
            'Customer Name': 'name',
            'Customer Email': 'email',
            'Customer Mobile Phone': 'mobile_phone'
        }
        self.order_headers = {
            'Order Number': 'order_number',
            'Customer ID': 'customer',
            'Status': 'status',
            'Order Date': 'order_date',
            'Total Price': 'total_price',
            'Order Items': 'order_items',
            'Refund Amount': 'refund_amount',
            'Balance': 'balance',
            'Last Refund Date': 'last_refund_date',
            'Total Products': 'total_products',
            'Total Treatments': 'total_treatments',
            'Total Packages': 'total_packages',
            'Total Series': 'total_series',
            'Total Gift Certificate Cards': 'total_gift_certificate_cards',
            'Total Cancellation Fee': 'total_cancellation_fee',
            'Total Discount Special': 'total_discount_special',
            'Tax': 'tax',
            'Tip': 'tip',
            'Total Tips': 'total_tips',
            'Prepaid Credit': 'prepaid_credit',
            'Refund': 'refund',
            'Payment Method': 'payment_method',
            'Created By': 'created_by',
        }
        self.customer_headers = {
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Street 1': 'street_1',
            'Street 2': 'street_2',
            'State': 'state',
            'City': 'city',
            'Postal Code': 'postal_code',
            'Email': 'email',
            'Primary Phone': 'primary_phone',
            'Work Phone': 'work_phone',
            'Home Phone': 'home_phone',
            'Mobile Phone': 'mobile_phone',
            'Receives Email': 'receives_email',
            'Receives SMS': 'receives_sms',
            'Status': 'status',
            'Date Created': 'date_created',
            'Birthday': 'birthday',
            'Login': 'login',
            'ID(GUID)': 'guid',
            'Customer ID': 'customer_id'
        }

    ###############################
    # UTILITY FUNCTIONS
    ###############################

    @staticmethod
    def add_location_to_df(df, file_path):
        location = os.path.basename(os.path.dirname(file_path))
        df['location'] = location

    def validate_dates_in_df_match_file_name(self, df, file_name, date_column):
        """Validate that the dates in the file name match the dates in the file
        This will warn us if an export had issues """
        start_date, end_date = self.get_dates_from_file_name(file_name)
        min_date = df[date_column].min()
        max_date = df[date_column].max()
        # if dates are NaN then df is empty
        if pd.isna(min_date) and pd.isna(max_date):
            return
        # if min or max date are pandas Timestamps, convert to date
        if type(min_date) == pd.Timestamp:
            min_date = min_date.date()
        if type(max_date) == pd.Timestamp:
            max_date = max_date.date()
        # Raise an error if df has any dates outside of the date range
        if min_date < start_date or max_date > end_date:
            raise ValueError(f'Dates in {file_name} do not match the date range in the file name')

    @staticmethod
    def get_dates_from_file_name(file_name):
        date_range = file_name.split(' ')[1].replace('.csv', '')
        dates = date_range.split('-')
        start_date = '-'.join(dates[:3])
        end_date = '-'.join(dates[3:])
        # start_date, end_date = date_range.split('_')
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        return start_date, end_date

    ###############################
    # EXCEPTIONS
    ###############################
    class InvalidFileException(Exception):
        pass

    ###############################
    # APPOINTMENTS
    ###############################
    def appointment_file_to_df(self, file_name):
        date_fields = ['Start Date/Time', 'End Date/Time']
        headers = {
            **self.appointment_headers,
            **self.appointment_customer_headers
        }
        df = pd.read_csv(
            file_name,
            usecols=headers.keys(),
            parse_dates=date_fields,
            converters={k: self.datetime_parser for k in date_fields}
        )
        df.rename(columns=headers, inplace=True)

        for date_field in ['Start Date/Time', 'End Date/Time']:
            renamed_header = headers[date_field]
            df[renamed_header] = df[renamed_header].astype(str)

        df.fillna('', inplace=True)
        self.add_location_to_df(df, file_name)
        return df

    def appointment_file_to_treatment_df(self, file_name):
        headers = {
            **self.appointment_treatment_headers,
            **self.appointment_customer_headers,
            'Booking Number': 'appointment'
        }
        df = pd.read_csv(
            file_name,
            usecols=list(headers.keys()),
            parse_dates=['Appointment On'],
            converters={
                'Appointment On': self.datetime_parser,
            }
        )
        df.rename(columns=headers, inplace=True)
        df['appointment_on'] = df['appointment_on'].astype(str)
        df['total'].replace('[\$,]', '', regex=True, inplace=True)
        df['tax'].replace('[\$,]', '', regex=True, inplace=True)
        df['price'].replace('[\$,]', '', regex=True, inplace=True)
        df.fillna('', inplace=True)
        return df

    def appointment_process(self, file_path):
        appointment_df = self.appointment_file_to_df(file_path)
        treatment_df = self.appointment_file_to_treatment_df(file_path)

        return appointment_df, treatment_df

    def import_appointments(self):
        # Get the appointments directory
        appointments_dir = os.path.join(self.directory, 'Appointment')

        # Get the list of files in the appointments directory
        locations = os.listdir(appointments_dir)

        appointments_dfs = []
        treatments_dfs = []
        # Loop through the files
        for location in locations:
            files = os.listdir(os.path.join(appointments_dir, location))
            for file in files:
                # Get the file path
                file_path = os.path.join(appointments_dir, location, file)
                try:
                    appointment_df, treatment_df = self.appointment_process(file_path)
                    appointments_dfs.append(appointment_df)
                    treatments_dfs.append(treatment_df)
                except Exception as e:
                    if self.invalid_file_handler:
                        self.invalid_file_handler.add_error(file_path, e)
                    else:
                        raise e

        # return appointment, treatment
        return pd.concat(appointments_dfs, ignore_index=True), pd.concat(treatments_dfs, ignore_index=True)

    ###############################
    # Orders
    ###############################
    def order_file_to_df(self, file_path):
        df = pd.read_csv(
            file_path,
            keep_default_na=False,
            escapechar='\\',
            parse_dates=['Order Date'],
            converters={'Order Date': self.date_parser},
            usecols=self.order_headers.keys(),
        )
        df.rename(columns=self.order_headers, inplace=True)
        df['order_date'] = df['order_date'].astype(str)
        for index in ['Total Price', 'Refund Amount', 'Balance', 'Total Products', 'Total Treatments',
                      'Total Packages', 'Total Series', 'Total Gift Certificate Cards', 'Total Cancellation Fee',
                      'Total Discount Special', 'Tax', 'Tip', 'Total Tips', 'Prepaid Credit']:
            df[self.order_headers[index]].replace('', '0.00', inplace=True)
            df[self.order_headers[index]].replace('[\$,]', '', regex=True, inplace=True)

        df['customer'].replace('[\{\}]', '', regex=True, inplace=True)
        df['last_refund_date'].replace({'': None}, inplace=True)

        self.add_location_to_df(df, file_path)
        # self.validate_dates_in_df_match_file_name(df, file_path, 'order_date')
        return df

    def import_orders(self):
        # Get the orders directory
        orders_dir = os.path.join(self.directory, 'Order')

        # Get the list of files in the orders directory
        locations = os.listdir(orders_dir)

        dfs = []
        for location in locations:
            # Get the list of files in the location directory
            files = os.listdir(os.path.join(orders_dir, location))
            # Loop through the files
            for file in files:
                # Get the file path
                file_path = os.path.join(orders_dir, location, file)
                try:
                    dfs.append(self.order_file_to_df(file_path))
                except Exception as e:
                    if self.invalid_file_handler:
                        self.invalid_file_handler.add_error(file_path, e)
                    else:
                        raise e

        return pd.concat(dfs, ignore_index=True)

    ###############################
    # Customers
    ###############################
    def customer_file_to_df(self, file_path):
        df = pd.read_csv(file_path, dtype=str)
        df.rename(columns=self.customer_headers, inplace=True)

        # Replace remaining NaN values with None
        df = df.where((pd.notnull(df)), None)

        # Remove Curly Braces from GUID
        df['guid'].replace('[\{\}]', '', regex=True, inplace=True)
        for index in [value for value in self.customer_headers.values() if 'phone' in value]:
            df[index].replace(r'\D', '', regex=True, inplace=True)

        return df

    def parse_customers(self):
        # Get the customers directory
        customers_dir = os.path.join(self.directory, 'Customer')
        # customers_dir = self.directory

        # Get the list of files in the customers directory
        files = os.listdir(customers_dir)

        dataframes = []
        for file in files:
            # Get the file path
            file_path = os.path.join(customers_dir, file)
            try:
                dataframes.append(self.customer_file_to_df(file_path))
            except Exception as e:
                if self.invalid_file_handler:
                    self.invalid_file_handler.add_error(file_path, e)
                else:
                    raise e

        return pd.concat(dataframes, ignore_index=True)
