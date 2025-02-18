import os
import sys
import hashlib
import requests
import logging
from io import StringIO
import datetime
from scraper import Scraper
import pytz

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    encoding='utf-8',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger.addHandler(logging.StreamHandler(sys.stdout))

def to_snake_case(text):
    # Replace spaces with underscores and convert to lowercase
    return text.lower().replace(' ', '_')


def convert_pst_time(time_str):
    # Parse the time string and set PST timezone
    pst = pytz.timezone('America/Los_Angeles')
    dt = datetime.strptime(time_str, '%m/%d/%Y %I:%M:%S %p')
    dt_pst = pst.localize(dt)
    # Convert to UTC ISO format for database compatibility
    return dt_pst.astimezone(pytz.UTC).isoformat()


def create_row_hash(row):
    # Strip any whitespace from values and handle potential missing values
    call_time = str(row.get('call_time', '')).strip()
    destination = str(row.get('destination', '')).strip()
    status = str(row.get('status', '')).strip()

    # Combine the specified columns and create a hash
    combined = f"{call_time}{destination}{status}"
    return hashlib.md5(combined.encode()).hexdigest()


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
        week_ago = datetime.datetime.now() - datetime.timedelta(days=368 * 2)
        scraper.set_date_filter(week_ago.date())
        if scraper.check_if_report_is_empty():
            logger.info("Report is empty")
            return
        scraper.set_table_size_100()
        page_count = scraper.get_pagination_count()
        logger.info(f"Found {page_count} pages")
        for page in range(1, page_count+1):
            scraper.navigate_to_pagination_page(page)
            csv_text = scraper.get_call_reports_table()
            logger.info("got call_reports_table")



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


