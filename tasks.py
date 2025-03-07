import os
import hashlib
import logging
import datetime
from scraper import Scraper
from db import Database

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    encoding='utf-8',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# logger.addHandler(logging.StreamHandler(sys.stdout))
db = Database()


def create_row_hash(row):
    # Strip any whitespace from values and handle potential missing values
    # expected rows: from_name, from, qos, dialed, to, qos, date, duration, download_url
    from_time = str(row.get('from_name', ''))
    destination = str(row.get('from', ''))
    date = str(row.get('date', ''))

    # Combine the specified columns and create a hash
    combined = f"{from_time}{destination}{date}"
    return hashlib.md5(combined.encode()).hexdigest()


def insert_df_into_db(df):
    """Insert records from a DataFrame into the database"""
    # Add hash ID to each row
    # df['id'] = df.apply(create_row_hash, axis=1)
    # # Convert timestamp to ISO format string
    # df['date'] = df['date'].apply(lambda x: x.isoformat() if pd.notnull(x) else None)    # Convert DataFrame to list of dictionaries
    calls_data = df.to_dict(orient='records')

    # Store in SQLite database
    db.insert_calls(calls_data)


def scrape_day_logged_in(scraper, date):
    scraper.set_date_filter(date)
    if scraper.check_if_report_is_empty():
        return
    scraper.set_table_size_100()
    page_count = scraper.get_pagination_count()

    for page in range(1, page_count+1):
        if page > 1:
            scraper.navigate_to_pagination_page(page)
        df = scraper.get_call_reports_table(date)
        insert_df_into_db(df)


def scrape_3cx(driver):
    DEBUG = os.environ.get('DEBUG') is not None
    scraper = Scraper(
        driver=driver,
        DEBUG=DEBUG
    )
    if DEBUG:
        logger.info("DEBUG mode is ON, clearing screenshot directory")
        scraper.clear_screenshot_directory()
    try:
        scraper.login(
            os.environ.get('ACCOUNT'),
            os.environ.get('PASSWORD'),
        )
        logger.info("Logged in")
        scraper.navigate_to_call_report_admin()
        logger.info("Navigating to call-report admin")


        # Define date range (e.g., last 30 days)
        # 
        end_date = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
        start_date = datetime.date(2025, 3, 2)

        # Iterate through each day in the range
        current_date = start_date
        while current_date <= end_date:
            logger.info(f"Scraping data for {current_date}")
            try:
                scrape_day_logged_in(scraper, current_date)
            except Exception as e:
                logger.error(f"Scraper encountered error, retrying day {current_date}.")
                scrape_day_logged_in(scraper, current_date)
            current_date += datetime.timedelta(days=1)

    except Exception as e:
        driver.quit()
        raise (e)


