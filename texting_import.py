import logging

import segment.analytics as analytics
import csv
from pprint import pprint

analytics.write_key = "eVCBVD5XUR4orBamwlcxJtQtvmJVg4QG"
analytics.debug = True
analytics.send = True

seg_logger = logging.getLogger('segment')
seg_logger.setLevel(logging.DEBUG)
seg_logger.addHandler(logging.StreamHandler())


with open("./downloads/text_unsub.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        analytics.object(object_id=row["Phone Number"][1:], collection="ez_text_unsub", properties={
            "date_added": row["Date Added"]
        })

