from scrapy.crawler import CrawlerProcess
from src.get_yearly_snapshot import get_yearly_snapshot
from src.utils.psql import get_site_by_id, get_connection
from src.spider import Spider
import time
import typer

app = typer.Typer(no_args_is_help=True)

@app.command(help="Starts the crawl", no_args_is_help=True)
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

    url = get_yearly_snapshot(year, site.start_url)

    print(f'Starting {url}')

    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ITEM_PIPELINES':
            { 'src.pipeline.DbPipeline': 300 } if push else { 'src.pipeline.StdoutPipeline': 300 },
        "DOWNLOAD_DELAY": "1.0",
        "CONCURRENT_REQUESTS_PER_DOMAIN": "1",
        'LOG_LEVEL': 'DEBUG' if verbose else 'INFO',
    })

    start = time.time()
    process.crawl(Spider, url, site)
    process.start()

    print(f'Took {time.time()- start} seconds')

if __name__ == "__main__":
    app()
