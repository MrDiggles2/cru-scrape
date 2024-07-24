import requests
import logging
import os.path
from typing import List
import pandas as pd
import re
from scrapy.crawler import CrawlerProcess
from spider import Spider


def parse_memento_line(line: str):
  # Define regex patterns to match URL, rel attribute, and datetime attribute
  url_pattern = r'<(.*?)>'
  rel_pattern = r'rel="(.*?)"'
  datetime_pattern = r'datetime="(.*?)"'

  # Use re.search to find matches
  url_match = re.search(url_pattern, line)
  rel_match = re.search(rel_pattern, line)
  datetime_match = re.search(datetime_pattern, line)

  # Extract matched groups
  url = url_match.group(1) if url_match else None
  rel = rel_match.group(1) if rel_match else None
  datetime_value = datetime_match.group(1) if datetime_match else None

  return url, rel, datetime_value

def get_yearly_snapshot(url: str) -> List[str] :
  slug = url.replace('http://', '').replace('https://', '').replace('.', '-').replace('/', '-')
  dirPath = os.path.dirname(os.path.realpath(__file__))
  dataPath = os.path.join(dirPath, slug) + '.txt'

  if not os.path.exists(dataPath):
    logging.debug(f'No data found for {url}, creating {dataPath}')
    response = requests.get(f"http://web.archive.org/web/timemap/link/{url}")

    if (response.status_code != 200):
      raise Exception(f"No snapshots found for url '${url}'")

    with open(dataPath, 'w') as f:
      f.write(response.text)

  with open(dataPath, 'r') as f:
    dataContent = f.read()
  
  dataRows = dataContent.strip().split('\n')
  parsedData = {"url": [], "rel": [], "datetime": []}

  for row in dataRows:
    url, rel, datetime = parse_memento_line(row)
    parsedData["url"].append(url)
    parsedData["rel"].append(rel)
    parsedData["datetime"].append(datetime)

  df = pd.DataFrame(parsedData)
  # Convert 'datetime' column to pandas datetime objects
  df['datetime'] = pd.to_datetime(df['datetime'])
  df["year"] = df['datetime'].dt.year

  # Filter for memento rows
  filtered_df = df[df['rel'].isin(['memento', 'first memento'])]

  # Group by year
  grouped = filtered_df.groupby('year')

  # Function to get middle row
  def get_middle_row(group):
      return group.iloc[len(group) // 2]

  return pd.concat([get_middle_row(group) for _, group in grouped])

url = "https://www.maine.gov/ifw/"
df = get_yearly_snapshot(url)

# Create a CrawlerProcess
process = CrawlerProcess(settings={
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'ITEM_PIPELINES': {
        'pipeline.MyPipeline': 300,
    },
    "DOWNLOAD_DELAY": "1.0",
    "CONCURRENT_REQUESTS_PER_DOMAIN": "1"
})

# Add your spider to the process
process.crawl(Spider, df.iloc[0])

# Start the crawling process
process.start()
