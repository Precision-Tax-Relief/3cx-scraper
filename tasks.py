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
# db = Database()


def create_row_hash(row):
    # Strip any whitespace from values and handle potential missing values
    # expected rows: from_name, from, qos, dialed, to, qos, date, duration, download_url
    from_time = str(row.get('from_time', '')).strip()
    destination = str(row.get('from', '')).strip()
    date = str(row.get('date', '').isoformat())

    # Combine the specified columns and create a hash
    combined = f"{from_time}{destination}{date}"
    return hashlib.md5(combined.encode()).hexdigest()


def insert_df_into_db(df):
    """Insert records from a DataFrame into the database"""
    # Add hash ID to each row
    df['id'] = df.apply(create_row_hash, axis=1)
    # Convert DataFrame to list of dictionaries
    calls_data = df.to_dict(orient='records')

    # Store in SQLite database
    db.insert_calls(calls_data)
    logger.info(f"Successfully stored {len(calls_data)} records in database")


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
        week_ago = datetime.datetime.now() - datetime.timedelta(days=5)
        scraper.set_date_filter(week_ago.date())
        if scraper.check_if_report_is_empty():
            logger.info("Report is empty")
            return
        scraper.set_table_size_100()
        page_count = scraper.get_pagination_count()
        dataframe = scraper.get_call_reports_table()
        logger.info("got call_reports_table")
        logger.info(f"Found {page_count} pages")
        insert_df_into_db(dataframe)
        # logger.info(csv_text)


        # for page in range(1, page_count+1):
        #     scraper.navigate_to_pagination_page(page)
        #     csv_text = scraper.get_call_reports_table()
        #     logger.info("got call_reports_table")



        # logger.info("Getting logs from one week ago")
        # week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        # scraper.set_date_filter(week_ago.date())
        # scraper.set_table_size_100()
        # csv_text = scraper.get_call_reports_table()
        # logger.info("got call_reports_table")
        # logger.info(csv_text)




    except Exception as e:
        driver.quit()
        raise (e)


