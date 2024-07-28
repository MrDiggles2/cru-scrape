from scrapy.crawler import CrawlerProcess
from get_yearly_snapshot import get_yearly_snapshot
from spider import Spider
import time
from twisted.internet import defer, reactor
import typer

app = typer.Typer(no_args_is_help=True)


@app.command(help="Starts the crawl")
def crawl(
    year: str = typer.Argument(..., help="The year of the site to scrape"),
    base_url: str = typer.Argument(..., help="The base url of the site to scrape")
):
    url = get_yearly_snapshot(year, base_url)

    print(f'Starting {url}')

    process = CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ITEM_PIPELINES': {
            'pipeline.MyPipeline': 300,
        },
        "DOWNLOAD_DELAY": "1.0",
        "CONCURRENT_REQUESTS_PER_DOMAIN": "1"
    })

    start = time.time()
    process.crawl(Spider, url)
    process.start()

    print(f'Took {time.time()- start} seconds')

if __name__ == "__main__":
    app()
