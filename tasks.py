import os
import sys
import hashlib
import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from scraper import Scraper
import pytz
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR, encoding='utf-8', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    scraper = Scraper(
        driver=driver
    )
    try:
        scraper.login(
            os.environ.get('ACCOUNT'),
            os.environ.get('PASSWORD'),
        )
        scraper.navigate_to_call_report_admin()
        csv_text = scraper.get_call_reports_table()

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
            on_bad_lines='error'
        )

        if df.empty:
            print("No data available in the CSV. Skipping further processing.")
            return  # Skip the rest of the function

        # Convert column names to snake case
        df.columns = [to_snake_case(col) for col in df.columns]

        # Log the column names for debugging
        logger.debug(f"DataFrame columns after conversion: {df.columns.tolist()}")

        # Convert call_time to UTC ISO format
        df['call_time'] = df['call_time'].apply(convert_pst_time)

        # Add hash ID to each row
        df['id'] = df.apply(create_row_hash, axis=1)

        # Convert DataFrame to JSON
        json_data = df.to_dict(orient='records')

        # Send POST request
        headers = {'Content-Type': 'application/json'}
        print('Sending data to ', OUT_URL)
        response = requests.post(OUT_URL, json=json_data, headers=headers)

        # Check if request was successful
        response.raise_for_status()
        print(f"Data successfully.")

    except pd.errors.EmptyDataError:
        logger.error("CSV text is empty or invalid")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data to {OUT_URL}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing data: {str(e)}")
        raise

    print("Job done")
