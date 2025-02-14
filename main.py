import os
import logging
import sys

import requests
from dotenv import load_dotenv

from webdriver_client import chrome_headless
from tasks import scrape_3cx


logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding='utf-8')
logger.addHandler(logging.StreamHandler(sys.stdout))
load_dotenv()

MISSING_ENVIRONMENT_VARIABLES = []

def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if not value:
        MISSING_ENVIRONMENT_VARIABLES.append(var_name)
    return value



ACCOUNT = get_env_variable('ACCOUNT')
PASSWORD =get_env_variable('PASSWORD')


def check_internet_connection(url="https://www.google.com", timeout=5):
    """Return True if there's an active internet connection."""
    try:
        response = requests.get(url, timeout=timeout)
        return True if response.status_code == 200 else False
    except requests.ConnectionError:
        return False

if __name__ == '__main__':
    if len(MISSING_ENVIRONMENT_VARIABLES) > 0:
        error = f'Internal Server Error - Missing environment variables: {", ".join(MISSING_ENVIRONMENT_VARIABLES)}'
        logger.error(error)
        raise Exception(error)
    if not check_internet_connection():
        error = f'No internet connection'
        logger.error(error)
        raise Exception(error)
    logger.debug('Internet connection is established')

    status_code = check_internet_connection()
    log = f'Internet connection status: {status_code}'
    logger.debug(log)
    driver = chrome_headless(logger)
    scrape_3cx(driver, logger)
    logger.info(f'Task completed')
    driver.quit()
