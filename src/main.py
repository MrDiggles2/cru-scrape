import typer
from dotenv import load_dotenv

from src.commands.crawl import crawl
from src.commands.seed_organizations import seed_organizations

load_dotenv()

def main():
  app = typer.Typer(no_args_is_help=True)

  app.command(
    short_help='Crawls a site for a given year',
    help="Given a site ID and year, crawls and scrapes a site, printing site contents to stdout by default",
    no_args_is_help=True
  )(crawl)

  app.command(
    short_help='Upserts organization and site records',
    help="Upserts organization and site records using organizations.tsv",
    no_args_is_help=False
  )(seed_organizations)

  app()

if __name__ == "__main__":
    main()