import os
from scraper import Scraper


def scrape_3cx(driver, logger):
    try:
        scraper = Scraper(
            driver=driver
        )
        scraper.login(
            os.environ.get('ACCOUNT'),
            os.environ.get('PASSWORD'),
        )
        logger.info("Logged in")
    except Exception as e:
        driver.quit()
        raise (e)