import time
import typer
from scrapy.crawler import CrawlerProcess

from src.get_yearly_snapshot import get_yearly_snapshot
from src.utils.psql import get_site_by_id, get_connection, get_inprogress_pages
from src.spider import Spider

def crawl(
    year: str = typer.Argument(..., help="The year of the site to scrape"),
    site_id: str = typer.Argument(..., help="ID of the site to scrap"),
    push: bool = typer.Option(False, "--push", is_flag=True, help="Push to DB"),
    verbose: bool = typer.Option(False, "--verbose", is_flag=True, help="Enable verbose logging")
):
  conn = get_connection()
  site = get_site_by_id(conn, site_id)

  if (site is None):
    raise Exception('No site found with ID {site_id}')

  start_urls = []
  inprogress_urls = get_inprogress_pages(conn, site, year)

  if len(inprogress_urls) > 0:
    start_urls = inprogress_urls
  else:
    start_urls = [get_yearly_snapshot(year, site.start_url)]

  print(f'Starting {start_urls}')

  process = CrawlerProcess(settings={
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'ITEM_PIPELINES':
        { 'src.pipeline.DbPipeline': 300 } if push else { 'src.pipeline.StdoutPipeline': 300 },
    "DOWNLOAD_DELAY": "1.0",
    "CONCURRENT_REQUESTS_PER_DOMAIN": "2",
    'LOG_LEVEL': 'DEBUG' if verbose else 'INFO',
  })

  start = time.time()
  process.crawl(Spider, start_urls, site, int(year), False, True)
  process.start()

  print(f'Took {time.time()- start} seconds')
