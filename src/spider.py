import scrapy
from scrapy.http import HtmlResponse, Response
from scrapy.spidermiddlewares.httperror import HttpError
from bs4 import BeautifulSoup
from bs4.element import Comment
import logging
import re
from typing import Optional, List, Tuple
from twisted.python.failure import Failure

from src.entities import Site, PageItem, StartPage
from src.waybackurl import WaybackUrl
from src.utils.psql import provision_empty_page, get_connection, upsert_page, record_failure_by_id, record_failure_by_url, already_visited
from src.ignore_list import should_ignore

class Spider(scrapy.Spider):
  name = 'spider'
  site: Optional[Site]
  start_pages: List[StartPage]
  year: Optional[int]
  stop_after_one = False
  push: bool

  def __init__(
    self,
    start_pages: List[StartPage],
    site: Optional[Site],
    year: Optional[int],
    stop_after_one: bool,
    push: bool,
    *args,
    **kwargs
  ):
    super().__init__(*args, **kwargs)
    self.site = site
    self.stop_after_one = stop_after_one
    self.year = year

    self.start_pages = start_pages
    # i.e. whether or not to push to DB
    self.push = push

    # Always suppress scrapy logs
    logging.getLogger('scrapy').setLevel(logging.ERROR)

  def start_requests(self):
    for page in self.start_pages:
      yield scrapy.Request(
        page.wb_url,
        dont_filter=True,
        meta={"page_id": page.id},
        errback=self.handle_error,
        callback=self.parse
      )

  def parse(self, response: Response):
    url = WaybackUrl.from_url(response.request.url)

    logging.info(f'at {url.get_full_url()}')

    # Scraped content
    content: Optional[str] = None
    # URLs uncovered on page
    next_urls: List[str] = []

    if url.is_pdf():
      # We should never navigate to a PDF page
      raise Exception(f'Tried to process pdf {url.get_original_url()}')
    elif isinstance(response, HtmlResponse):
      content, next_urls = self.handle_html(response)
    else:
      # All responses should be of type HtmlResponse but just in case, log it as
      # a warning so we can come back to it
      logging.warning(f'Got type {type(response)} for {url.get_full_url()}, skipping')

    # Pass the scraped content along to the pipeline
    if content is not None:
      item = PageItem()
      item['page_id'] = response.meta['page_id']
      item['wb_url'] = str(url.get_full_url())
      item['content'] = content
      item['site_id'] = getattr(self.site, 'id', None)
      yield item

    if self.stop_after_one:
      if len(next_urls) > 0:
        logging.info('Stopping after one, would have followed to:')
      else:
        logging.info('Stopping after one, no further links found')

    for next_url in next_urls:
      next_wb_url = url.join(next_url)

      # Check each URL to see if we need to follow it
      if not self.is_relevant(next_wb_url):
        continue

      if self.stop_after_one:
        logging.info(f'\t{next_wb_url.get_full_url()}')
        continue

      # Provision row for this page
      page_id = None
      if self.push:
        with get_connection() as conn:
          page_id = provision_empty_page(conn, self.site, next_wb_url)

          # Fill in PDFs with empty strings so we never navigate to (and
          # download) PDFs. We'll need to go back and redo these at a later
          # time.
          if next_wb_url.is_pdf():
            item = PageItem()
            item['page_id'] = page_id
            item['content'] = ''
            item['wb_url'] = str(next_wb_url.get_full_url())
            item['site_id'] = getattr(self.site, 'id', None)
            upsert_page(conn, item)

      if not next_wb_url.is_pdf():
        yield scrapy.Request(
          next_wb_url.get_full_url(),
          dont_filter=True,
          meta={"page_id": page_id},
          errback=self.handle_error,
          callback=self.parse
        )

  def handle_error(self, failure: Failure):
    error_message = repr(failure)

    if failure.check(HttpError):
        response = failure.value.response
        page_id = response.meta['page_id']

        self.logger.error(f'at {response.request.url}: {error_message}')

        with get_connection() as conn:
          if page_id:
            record_failure_by_id(conn, page_id, error_message)
          else:
            url = WaybackUrl.from_url(response.request.url)
            record_failure_by_url(conn, url.get_original_url(), error_message)
    else:
      self.logger.error(f'unknown error: {failure.getErrorMessage()}\n{failure.getTraceback}')

  def handle_html(self, response: HtmlResponse) -> Tuple[Optional[str], List[str]]:

    soup = BeautifulSoup(response.body, 'html.parser')

    # Remove wayback machine elements

    def decompose_if_exists(element):
      if element:
        element.decompose()

    decompose_if_exists(soup.find('div', id='wm-ipp-base'))
    decompose_if_exists(soup.find('div', id='wm-ipp-print'))

    # Grab all text from visible elements

    def tag_filter(element):
      if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
          return False
      if isinstance(element, Comment):
          return False
      return True

    texts = soup.findAll(text=True)
    visible_texts = filter(tag_filter, texts)  

    # Join them all together
    joined_text = u" ".join(visible_texts)

    # Remove any consecutive whitespaces
    stripped_text = re.sub(r'\s+', ' ', joined_text).strip()

    # Send back any links we find in the document
    links = []
    for element in soup.find_all('a', href=True):
      links.append(element['href'])

    return (stripped_text, links)

  def is_relevant(self, link: WaybackUrl):

    logging.debug(f'Checking relevance of {link.get_full_url()}')

    if should_ignore(link.get_original_url()):
      logging.debug(f'\tContains an ignore fragment')
      return True

    # Check that we're staying on the page where we started

    if self.site and not link.contains(self.site.base_url):
      logging.debug(f'\tDoes not contain start URL')
      return False

    # Check that the year on the link is within one year of our start URL

    if not self.matches_year(link):
      logging.debug(f'\tDoes not match year')
      return False

    with get_connection() as conn:
      if already_visited(conn, link.get_original_url(), link.get_snapshot_date().year):
        logging.debug(f'\tAlready visited a previous snapshot')
        return False

    logging.debug(f'\tGood')

    return True

  def matches_year(self, link: WaybackUrl):
    return self.year is None or link.matches_year(self.year, plus_minus=0)