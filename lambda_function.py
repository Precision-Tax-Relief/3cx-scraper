from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def check_internet_connection(url="https://www.google.com", timeout=5):
    """Return True if there's an active internet connection, False otherwise."""
    try:
        response = requests.get(url, timeout=timeout)
        return True if response.status_code == 200 else False
    except requests.ConnectionError:
        return False


def handler(event, context):
    if not check_internet_connection():
        return {
            'statusCode': 500,
            'message': 'Internal Server Error - No internet connection'
        }
    logger.info('Internet connection is established')


    # Define Chrome options to open the browser in headless mode
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.binary_location = os.path.join(os.getcwd(), "chrome-linux64", "chrome")
    logger.info(f'{options.binary_location = }')
    logger.info(f'{os.path.isfile(options.binary_location) = }')

    # Setup ChromeDriver
    chrome_driver_binary = os.path.join(os.getcwd(), "chromedriver-linux64", "chromedriver")
    service = Service(os.path.join(os.getcwd(), "chromedriver-linux64", "chromedriver"))
    logger.info(f'{chrome_driver_binary = }')
    logger.info(f'{os.path.isfile(chrome_driver_binary) = }')
    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 500,
            'message': 'Internal Server Error - Failed to initialize ChromeDriver'
        }

    driver.get('https://www.google.com')

    title = driver.title
    html = driver.page_source

    # Close the browser!
    driver.quit()

    return {
        'statusCode': 200,
        'body': {
            'title': title,
            'html': html
        }
    }
