from scrapy.crawler import CrawlerProcess
from get_yearly_snapshot import get_yearly_snapshot
from spider import Spider
import time

baseUrls = [
  "https://www.maine.gov/ifw/"
]

for baseUrl in baseUrls:
  urls = get_yearly_snapshot(baseUrl)

  for url in urls:

    print(f'Starting {url}')

    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ITEM_PIPELINES': {
            'pipeline.MyPipeline': 300,
        },
        "DOWNLOAD_DELAY": "1.0",
        "CONCURRENT_REQUESTS_PER_DOMAIN": "1"
    })

    process.crawl(Spider, url)

    start = time.time()
    process.start()
    print(f'Took {time.time()- start} seconds')