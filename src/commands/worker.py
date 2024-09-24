from rq import Worker
from src.commands.crawl import crawl
from src.utils.redis import get_connection

def worker():
  # Provide the worker with the list of queues (str) to listen to.
  w = Worker(['default'], connection=get_connection())
  w.work()

def handle_site(args):
  year, site_id = args
  crawl(year, site_id, push = False, verbose = False, concurrency = 2)
