from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
import os

logging.getLogger('segment').setLevel('DEBUG')

def chrome_headless(logger, download_dir=None):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")

    # Use environment variables for Chrome binary and ChromeDriver paths
    chrome_binary = os.getenv('CHROME_BINARY', '/usr/bin/chromium-browser')
    chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')

    options.binary_location = chrome_binary

    # Set download directory
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    if download_dir is not None:
        prefs["download.default_directory"] = download_dir
    options.add_experimental_option('prefs', prefs)

    # Setup ChromeDriver
    service = Service(chromedriver_path)
    logger.info(f'ChromeDriver path: {chromedriver_path}')
    logger.info(f'Chrome binary path: {chrome_binary}')

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        logger.error(f'Failed to initialize Chrome driver: {str(e)}')
        raise e

    driver.maximize_window()
    return driver

def chrome_testing(download_dir=None):
    options = Options()
    prefs = {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    if download_dir is not None:
        prefs["download.default_directory"] = download_dir
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver
