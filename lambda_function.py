import os
import sys
import logging
import requests
from dotenv import load_dotenv
import signal

from webdriver_client import chrome_headless, chrome_testing
from tasks import customers_today, daily_scrape, weekly_scrape, monthly_scrape
from tempfile import TemporaryDirectory
import segment.analytics as analytics

logger_seg = logging.getLogger('segment')
logger_seg.setLevel(logging.DEBUG)
logger_seg.addHandler(logging.StreamHandler(sys.stdout))

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)
load_dotenv()

BOOKER_ACCOUNT = os.environ.get('BOOKER_ACCOUNT')
BOOKER_USERNAME = os.getenv('BOOKER_USERNAME')
BOOKER_PASSWORD = os.getenv('BOOKER_PASSWORD')
ENVIRONMENT = os.getenv('ENVIRONMENT')
SEGMENT_WRITE_KEY = os.getenv('SEGMENT_WRITE_KEY')

if SEGMENT_WRITE_KEY is None:
    logger.error('SEGMENT_WRITE_KEY must be set in environment variables')
    raise ValueError('SEGMENT_WRITE_KEY must be set in environment variables')

if ENVIRONMENT is None:
    logger.info('ENVIRONMENT is not set in environment variables, defaulting to "test"')
    ENVIRONMENT = 'test'

if any(var is None for var in [BOOKER_ACCOUNT, BOOKER_USERNAME, BOOKER_PASSWORD, SEGMENT_WRITE_KEY]):
    logger.error('BOOKER_ACCOUNT, BOOKER_USERNAME, BOOKER_PASSWORD, and SEGMENT_WRITE_KEY' +
                 'must be set in environment variables' +
                 f'\n{BOOKER_ACCOUNT = }' +
                 f'\n{BOOKER_USERNAME = }' +
                 f'\n{BOOKER_PASSWORD = }' +
                 f'\n{SEGMENT_WRITE_KEY = }'
                 )
    raise ValueError('BOOKER_ACCOUNT, BOOKER_USERNAME, and BOOKER_PASSWORD must be set in environment variables')

analytics.write_key = SEGMENT_WRITE_KEY
analytics.debug = True
analytics.send = True

def timeout_handler(signum, frame):
    raise TimeoutError("Timout reached")

# Set the signal handler
signal.signal(signal.SIGALRM, timeout_handler)


def check_internet_connection(url="https://www.google.com", timeout=5):
    """Return True if there's an active internet connection."""
    try:
        response = requests.get(url, timeout=timeout)
        return True if response.status_code == 200 else False
    except requests.ConnectionError:
        return False


TASKS = {
    'customers_today': customers_today,
    'daily': daily_scrape,
    'weekly': weekly_scrape,
    'monthly': monthly_scrape,
}


def handler(event, context):
    if not check_internet_connection():
        return {
            'statusCode': 500,
            'message': 'Internal Server Error - No internet connection'
        }
    logger.debug('Internet connection is established')

    event = event or {}
    task = event.get('task', None)
    if task is None:
        return {
            'statusCode': 400,
            'message': 'Bad Request - No task specified'
        }
    task_func = TASKS.get(task, None)
    if task_func is None:
        return {
            'statusCode': 400,
            'message': 'Bad Request - Task not found'
        }

    with TemporaryDirectory() as download_dir:
        if ENVIRONMENT == 'test':
            driver = chrome_testing(download_dir)
        else:
            driver = chrome_headless(logger, download_dir)

        try:
            task_func(driver, download_dir, analytics)
        except Exception as e:
            driver.quit()
            logger.error(f'Error in task {task}: {e}')
            return {
                'statusCode': 500,
                'message': f'Internal Server Error - Error in task {task}: {e}'
            }

    driver.quit()

    try:
        signal.alarm(30)
        analytics.shutdown()
    except TimeoutError as e:
        logger.error("Analytics shutdown took too long")
        return {
            'statusCode': 500,
            'message': 'Internal Server Error - Analytics shutdown took too long'
        }

    return {
        'statusCode': 200,
    }


if __name__ == '__main__':
    handler({'task': 'daily'}, None)