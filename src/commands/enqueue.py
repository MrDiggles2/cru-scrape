import typer
from rq import Queue

from src.commands.worker import handle_site
from src.utils.redis import get_connection

def enqueue(
  year: str = typer.Argument(..., help="The year of the site to scrape"),
  site_id: str = typer.Argument(..., help="ID of the site to scrap"),
  at_front: bool = typer.Option(False, "--at-front", is_flag=True, help="Pushes task to the front of the queue"),
):
  redis_conn = get_connection()
  queue = Queue(connection=redis_conn)

  queue.enqueue(handle_site, (year, site_id), at_front=at_front)
