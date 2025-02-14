import os
import hashlib
import requests
import pandas as pd
from io import StringIO
from scraper import Scraper


def create_row_hash(row):
    # Strip any whitespace from values and handle potential missing values
    call_time = str(row.get('Call Time', '')).strip()
    destination = str(row.get('Destination', '')).strip()
    status = str(row.get('Status', '')).strip()

    # Combine the specified columns and create a hash
    combined = f"{call_time}{destination}{status}"
    return hashlib.md5(combined.encode()).hexdigest()

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
        scraper.navigate_to_call_report_admin()
        logger.info("Navigating to call-report admin")
        csv_text = scraper.get_call_reports_table()
        logger.info("got call_reports_table")

    except Exception as e:
        driver.quit()
        raise (e)

    driver.quit()

    OUT_URL = os.environ.get('OUT_URL')

    try:
        # Convert CSV string to DataFrame
        df = pd.read_csv(
            StringIO(csv_text),
            skipinitialspace=True,
            on_bad_lines='warn'
        )

        # Log the column names for debugging
        logger.debug(f"DataFrame columns: {df.columns.tolist()}")

        # Add hash ID to each row
        df['id'] = df.apply(create_row_hash, axis=1)

        # Convert DataFrame to JSON
        json_data = df.to_dict(orient='records')

        # Send POST request
        headers = {'Content-Type': 'application/json'}
        response = requests.post(OUT_URL, json=json_data, headers=headers)

        # Check if request was successful
        response.raise_for_status()
        logger.info(f"Data successfully sent to {OUT_URL}")

    except pd.errors.EmptyDataError:
        logger.error("CSV text is empty or invalid")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data to {OUT_URL}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing data: {str(e)}")
        raise
