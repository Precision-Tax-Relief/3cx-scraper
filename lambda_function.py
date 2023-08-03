from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os

def handler(event, context):
    # Define Chrome options to open the browser in headless mode
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1200")
    options.binary_location = os.path.join(os.getcwd(), "chrome-linux64", "chrome")

    # Setup ChromeDriver
    service = Service(os.path.join(os.getcwd(), "chromedriver-linux64", "chromedriver"))
    driver = webdriver.Chrome(service=service, options=options)

    driver.get('https://www.google.com')

    print(driver.title)

    # Close the browser!
    driver.quit()

    return {
        'statusCode': 200,
        'body': 'Headless Chrome Initialized'
    }
