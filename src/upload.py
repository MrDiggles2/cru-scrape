import psycopg2
import json
import os
import re
from dotenv import load_dotenv
from waybackurl import WaybackUrl
 
load_dotenv()

conn = psycopg2.connect(
    database="scrape_results",
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port='5432'
)
 
cursor = conn.cursor()

sql = """
INSERT INTO scrape_results (base_url, year, original_url, wb_url, content, original_timestamp)
VALUES (%s, %s, %s, %s, %s, %s)
"""

with open('../output/1722824728.ndjson', 'r') as f:
  for line in f:
    data = json.loads(line)
    url = WaybackUrl.from_url(data["url"])
    base_url = WaybackUrl.from_url(data["base_url"])

    processed_string = re.sub(r'\s+', ' ', data["content"])

    cursor.execute(
      sql,
      (
        base_url.get_original_url(),
        url.get_snapshot_date().year,
        url.get_original_url(),
        url.get_full_url(),
        processed_string,
        url.get_snapshot_date()
      )
    )

conn.commit()
conn.close()