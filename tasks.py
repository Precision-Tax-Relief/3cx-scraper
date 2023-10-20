import os
import datetime
from scrapers import BookerScraper
from parser import BookerParser
from tempfile import TemporaryDirectory
import hashlib
import uuid


def string_to_uuid(s):
    sha1 = hashlib.sha1(s.encode())
    # Take the first 16 bytes from the SHA-1 hash to create the UUID.
    return str(uuid.UUID(bytes=sha1.digest()[:16]))


def send_customers(dataframe, analytics):
    for row in dataframe.iterrows():
        data = dict(row[1])
        analytics.object(object_id=data['guid'], collection='customers', properties=data)


def send_appointments(appointment_dataframe, treatment_dataframe, analytics):
    for row in appointment_dataframe.iterrows():
        data = dict(row[1])
        analytics.object(object_id=data['booking_number'], collection='appointments', properties=data)

    for row in treatment_dataframe.iterrows():
        data = dict(row[1])
        analytics.object(object_id=string_to_uuid(f'{data["appointment"]}{data["appointment_on"]}'),
                         collection='appointments',
                         properties=data)


def send_orders(dataframe, analytics):
    for row in dataframe.iterrows():
        data = dict(row[1])
        analytics.object(object_id=data['order_number'], collection='orders', properties=data)


def customers_today(driver, download_dir, analytics):
    with TemporaryDirectory() as dest_dir:
        try:
            scraper = BookerScraper(
                driver=driver,
                start_date=datetime.date.today() - datetime.timedelta(days=1),
                end_date=datetime.date.today() + datetime.timedelta(days=1),
                download_dir=download_dir,
                destination_dir=dest_dir,
            )
            scraper.login(
                os.environ.get('BOOKER_ACCOUNT'),
                os.environ.get('BOOKER_USERNAME'),
                os.environ.get('BOOKER_PASSWORD')
            )
            scraper.customer_added_today_flow()
        except Exception as e:
            driver.quit()
            raise (e)

        parser = BookerParser(dest_dir)
        df = parser.parse_customers()
    send_customers(df, analytics)
    return f'Imported {len(df)} customers from today.'


def daily_scrape(driver, download_dir, analytics):
    with TemporaryDirectory() as dest_dir:
        try:
            scraper = BookerScraper(
                driver=driver,
                start_date=datetime.date.today() - datetime.timedelta(days=1),
                end_date=datetime.date.today(),
                download_dir=download_dir,
                destination_dir=dest_dir,
                export_period=2
            )
            scraper.login(
                os.environ.get('BOOKER_ACCOUNT'),
                os.environ.get('BOOKER_USERNAME'),
                os.environ.get('BOOKER_PASSWORD')
            )
            scraper.customer_added_today_flow()
            parser = BookerParser(dest_dir)
            df = parser.parse_customers()
        except Exception as e:
            driver.quit()
            raise (e)
    send_customers(df, analytics)

    for location in scraper.locations.values():
        with TemporaryDirectory() as dest_dir:
            scraper.destination_dir = dest_dir
            scraper.appointments_flow(location, date_type='date_created')
            parser = BookerParser(dest_dir)
            a_df, t_df = parser.import_appointments()
        send_appointments(a_df, t_df, analytics)

        with TemporaryDirectory() as dest_dir:
            scraper.destination_dir = dest_dir
            scraper.orders_flow(location)
            parser = BookerParser(dest_dir)
            df = parser.import_orders()
        send_orders(df, analytics)


def weekly_scrape(driver, download_dir, analytics):
    with TemporaryDirectory() as dest_dir:
        try:
            scraper = BookerScraper(
                driver=driver,
                start_date=datetime.date.today() - datetime.timedelta(days=7),
                end_date=datetime.date.today() + datetime.timedelta(days=7),
                download_dir=download_dir,
                destination_dir=dest_dir,
                export_period=8
            )
            scraper.login(
                os.environ.get('BOOKER_ACCOUNT'),
                os.environ.get('BOOKER_USERNAME'),
                os.environ.get('BOOKER_PASSWORD')
            )
            scraper.customer_added_last_week_flow()
            parser = BookerParser(dest_dir)
            df = parser.parse_customers()
        except Exception as e:
            driver.quit()
            raise (e)
    send_customers(df, analytics)

    for location in scraper.locations.values():
        with TemporaryDirectory() as dest_dir:
            scraper.destination_dir = dest_dir
            scraper.appointments_flow(location)
            parser = BookerParser(dest_dir)
            a_df, t_df = parser.import_appointments()
        send_appointments(a_df, t_df, analytics)

        with TemporaryDirectory() as dest_dir:
            scraper.destination_dir = dest_dir
            scraper.orders_flow(location)
            parser = BookerParser(dest_dir)
            df = parser.import_orders()
        send_orders(df, analytics)


def monthly_scrape(driver, download_dir, analytics):
    with TemporaryDirectory() as dest_dir:
        try:
            scraper = BookerScraper(
                driver=driver,
                start_date=datetime.date.today() - datetime.timedelta(days=32),
                end_date=datetime.date.today() + datetime.timedelta(days=32),
                download_dir=download_dir,
                destination_dir=dest_dir,
                export_period=10
            )
            scraper.login(
                os.environ.get('BOOKER_ACCOUNT'),
                os.environ.get('BOOKER_USERNAME'),
                os.environ.get('BOOKER_PASSWORD')
            )
            scraper.customer_flow()
            parser = BookerParser(dest_dir)
            df = parser.parse_customers()
        except Exception as e:
            driver.quit()
            raise (e)
    send_customers(df, analytics)

    for location in scraper.locations.values():
        with TemporaryDirectory() as dest_dir:
            scraper.destination_dir = dest_dir
            scraper.appointments_flow(location)
            parser = BookerParser(dest_dir)
            a_df, t_df = parser.import_appointments()
        send_appointments(a_df, t_df, analytics)

        with TemporaryDirectory() as dest_dir:
            scraper.destination_dir = dest_dir
            scraper.orders_flow(location)
            parser = BookerParser(dest_dir)
            df = parser.import_orders()
        send_orders(df, analytics)


def customer_weekly_scrape(driver, download_dir, analytics):
    with TemporaryDirectory() as dest_dir:
        try:
            scraper = BookerScraper(
                driver=driver,
                start_date=datetime.date(2021, 8, 6),
                end_date=datetime.date.today() + datetime.timedelta(days=30),
                download_dir=download_dir,
                destination_dir=dest_dir,
            )
            scraper.login(
                os.environ.get('BOOKER_ACCOUNT'),
                os.environ.get('BOOKER_USERNAME'),
                os.environ.get('BOOKER_PASSWORD')
            )
            scraper.customer_added_last_week_flow()
        except Exception as e:
            driver.quit()
            raise (e)
        parser = BookerParser(dest_dir)
        df = parser.parse_customers()
        send_customers(df, analytics)


def appointments_test(driver, download_dir, analytics):
    with TemporaryDirectory() as dest_dir:
        try:
            scraper = BookerScraper(
                driver=driver,
                start_date=datetime.date.today() - datetime.timedelta(days=60),
                end_date=datetime.date.today() + datetime.timedelta(days=30),
                download_dir=download_dir,
                destination_dir=dest_dir,
            )
            scraper.login(
                os.environ.get('BOOKER_ACCOUNT'),
                os.environ.get('BOOKER_USERNAME'),
                os.environ.get('BOOKER_PASSWORD')
            )
            scraper.appointments_flow(scraper.locations['cda'])
            scraper.appointments_flow(scraper.locations['ll'])
        except Exception as e:
            driver.quit()
            raise (e)
        parser = BookerParser(dest_dir)
        a_df, t_df = parser.import_appointments()

    send_appointments(a_df, t_df, analytics)


def order_test(driver, download_dir, analytics):
    with TemporaryDirectory() as dest_dir:
        try:
            scraper = BookerScraper(
                driver=driver,
                start_date=datetime.date.today() - datetime.timedelta(days=14),
                end_date=datetime.date.today() + datetime.timedelta(days=2),
                download_dir=download_dir,
                destination_dir=dest_dir,
            )
            scraper.login(
                os.environ.get('BOOKER_ACCOUNT'),
                os.environ.get('BOOKER_USERNAME'),
                os.environ.get('BOOKER_PASSWORD')
            )
            scraper.orders_flow(scraper.locations['cda'])
            scraper.orders_flow(scraper.locations['ll'])
        except Exception as e:
            driver.quit()
            raise (e)
        parser = BookerParser(dest_dir)
        df = parser.import_orders()
