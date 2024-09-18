import time
import typer
from scrapy.crawler import CrawlerProcess

from src.get_yearly_snapshot import get_yearly_snapshot
from src.utils.psql import get_site_by_id, get_connection, get_inprogress_pages
from src.spider import Spider
from src.entities import StartPage

def crawl(
    year: str = typer.Argument(..., help="The year of the site to scrape"),
    site_id: str = typer.Argument(..., help="ID of the site to scrap"),
    push: bool = typer.Option(False, "--push", is_flag=True, help="Push to DB"),
    verbose: bool = typer.Option(False, "--verbose", is_flag=True, help="Enable verbose logging"),
    concurrency: int = typer.Option(2, "--concurrency", help="Number of concurrent requests to make"),
):
  conn = get_connection()
  site = get_site_by_id(conn, site_id)

  if (site is None):
    raise Exception('No site found with ID {site_id}')

  start_pages = []
  inprogress_pages = get_inprogress_pages(conn, site, year)

  if len(inprogress_pages) > 0:
    start_pages = inprogress_pages
    print('Detected interrupted job, starting up from last known pages:')
    for page in start_pages:
      print(f'\t{page.id}\t{page.wb_url}')
  else:
    start_wb_url = get_yearly_snapshot(year, site.start_url)
    start_pages = [StartPage({'id': None, 'wb_url': start_wb_url })]
    print(f'Starting new job for site {site.id} at URL {start_wb_url}')

  print('\n')

  process = CrawlerProcess(settings={
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'ITEM_PIPELINES':
        { 'src.pipeline.DbPipeline': 300 } if push else { 'src.pipeline.StdoutPipeline': 300 },
    "DOWNLOAD_DELAY": "0.25",
    "CONCURRENT_REQUESTS_PER_DOMAIN": str(concurrency),
    'LOG_LEVEL': 'DEBUG' if verbose else 'INFO',
    'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
  })

  start = time.time()
  process.crawl(Spider, start_pages, site, int(year), False, push)
  process.start()

  print(f'Took {time.time()- start} seconds')
