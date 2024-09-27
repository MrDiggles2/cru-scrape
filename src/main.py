import typer
from dotenv import load_dotenv

from src.commands.crawl import crawl
from src.commands.seed_organizations import seed_organizations
from src.commands.scrape_one_url import scrape_one_url
from src.commands.worker import worker
from src.commands.enqueue import enqueue
from src.commands.list_combos import list_combos

load_dotenv()

def main():
  app = typer.Typer(no_args_is_help=True)

  app.command(
    short_help='Crawls a site for a given year',
    help="Given a site ID and year, crawls and scrapes a site, printing site contents to stdout by default",
    no_args_is_help=True
  )(crawl)

  app.command(
    short_help='Scrapes a single wayback URL and prints the result. Does not push to DB.',
    help="Scrapes a single wayback URL and prints the result. Does not push to DB.",
    no_args_is_help=True
  )(scrape_one_url)

  app.command(
    short_help='Upserts organization and site records',
    help="Upserts organization and site records using organizations.tsv",
    no_args_is_help=False
  )(seed_organizations)

  app.command(
    short_help='Starts a worker to crawl based off of a shared queue',
    help="Starts a worker to crawl based off of a shared queue",
    no_args_is_help=False
  )(worker)

  app.command(
    short_help='Enqueues a job for workers to pickup',
    help="Enqueues a job for workers to pickup",
    no_args_is_help=True
  )(enqueue)

  app.command(
    short_help='FIXME',
    help="FIXME",
    no_args_is_help=False
  )(list_combos)

  app()

if __name__ == "__main__":
    main()