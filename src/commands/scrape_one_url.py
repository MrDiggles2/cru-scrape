import time
import typer
from scrapy.crawler import CrawlerProcess

from src.spider import Spider
from src.waybackurl import WaybackUrl

def scrape_one_url(
    url: str = typer.Argument(..., help="The Wayback URL to scrape"),
    verbose: bool = typer.Option(False, "--verbose", is_flag=True, help="Enable verbose logging")
):

  wb_url = WaybackUrl(url)

  if not wb_url.is_valid():
    raise Exception(f'{url} is not a valid Wayback URL')

  print(f'Starting {url}')

  process = CrawlerProcess(settings={
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'ITEM_PIPELINES': { 'src.pipeline.StdoutPipeline': 300 },
    "DOWNLOAD_DELAY": "1.0",
    "CONCURRENT_REQUESTS_PER_DOMAIN": "1",
    'LOG_LEVEL': 'DEBUG' if verbose else 'INFO',
  })

  start = time.time()
  process.crawl(Spider, url, None, None, True, False)
  process.start()

  print(f'Took {time.time()- start} seconds')
