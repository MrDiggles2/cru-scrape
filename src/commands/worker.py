from rq import Worker
import typer

from src.commands.crawl import crawl
from src.utils.redis import get_connection
from src.utils.env_var import set_if_missing

should_push = False

def worker(
  name: str = typer.Option('Whodat', "--name", is_flag=True, help="Name of the worker"),
  push: bool = typer.Option(False, "--push", is_flag=True, help="Push to DB"),
):
  global should_push
  should_push = push

  # Something about rq and scrapy fails if this isn't set
  set_if_missing("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")
  # Log level gets set to DEBUG for some reason
  set_if_missing("LOG_LEVEL", "INFO")

  # Provide the worker with the list of queues (str) to listen to.
  w = Worker(['default'], connection=get_connection(), name=name)
  w.work()

def handle_site(args):
  global should_push

  year, site_id = args
  crawl(year, site_id, push = should_push, verbose = False, concurrency = 2)
