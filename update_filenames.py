from db import  Database
import requests
from urllib.parse import unquote
from time import sleep

db = Database()

def get_filename_from_headers(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        try:
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"{str(e)}")
            return str(response.status_code)

        # Try to get filename from Content-Disposition header
        if 'Content-Disposition' in response.headers:
            cd = response.headers['Content-Disposition']
            if 'filename=' in cd:
                filename = cd.split('filename=')[1].strip('"')
                return unquote(filename)

        return None
    except requests.RequestException as e:
        print(f"{str(e)}")
        return "500"

while True:
    records = db.get_records_without_filename(order="asc")
    print(f"Found {len(records)} records to process")

    updates = []
    batch_size = 100

    for id, url, filename in records:
        has_updates = True
        if filename is not None:
            raise BaseException(f"Record {id} already has a filename")

        filename = get_filename_from_headers(url)

        if filename is None:
            continue

        print(f"Record {id}: {filename}")

        updates.append((filename, id))
        if len(updates) >= batch_size:
            print("\n###############\n")
            db.update_filenames_batch(updates)
            print("\n###############\n")
            updates = []
        sleep(0.001)

    print("\n###############\n")
    db.update_filenames_batch(updates)
    print("\n###############\n")
    print("Reached End of loop. Sleeping...")
    print("\n###############\n")

    sleep(10)




