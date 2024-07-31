import psycopg2
import json
import re
from waybackurl import WaybackUrl
 
conn = psycopg2.connect(
    database="scrape_results",
    user='postgres',
    password='A&3!U0m9Md5qS#3l',
    host='cru-scrape.c9su4260u1a7.us-east-1.rds.amazonaws.com',
    port='5432'
)
 
cursor = conn.cursor()

sql = """
INSERT INTO scrape_results (base_url, year, original_url, wb_url, content, original_timestamp)
VALUES (%s, %s, %s, %s, %s, %s)
"""

with open('../output/1721853210.ndjson', 'r') as f:
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