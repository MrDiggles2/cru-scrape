import scrapy
from scrapy.http import HtmlResponse, Response
from bs4 import BeautifulSoup
from bs4.element import Comment
import logging
import re
from typing import Optional, List, Tuple

from src.entities import Site, PageItem
from src.waybackurl import WaybackUrl
from src.utils.psql import provision_empty_pages, get_connection

class Spider(scrapy.Spider):
  name = 'spider'
  site = Site
  start_urls = []
  year: int
  visited = set()
  on_first_page = True
  stop_after_one = False
  push: bool

  def __init__(
    self,
    start_urls: List[str],
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

    # This is how scrapy knows where to scrape
    self.start_urls = start_urls
    # i.e. whether or not to push to DB
    self.push = push

    # Always suppress scrapy logs
    logging.getLogger('scrapy').setLevel(logging.ERROR)

  def parse(self, response: Response):
    url = WaybackUrl.from_url(response.request.url)

    logging.info(f'at {url.get_full_url()}')

    # Scraped content
    content: Optional[str] = None
    # URLs uncovered on page
    next_urls: List[str] = []

    if self.year is not None and not url.matches_year(self.year):
      # We need to check here since WB will occasionally redirect to a different
      # year. If we encounter those, we should just ignore it to avoid muddling
      # up the data.
      logging.info('Got redirected to a different year, skipping')
    elif isinstance(response, HtmlResponse):
      if url.get_original_url().lower().endswith('.pdf'):
        content, next_urls = self.handle_pdf(response)
      else:
        content, next_urls = self.handle_html(response)
    else:
      # All responses should be of type HtmlResponse but just in case, log it as
      # a warning so we can come back to it
      logging.warning(f'Got type {type(response)} for {url.get_full_url()}, skipping')

    # Pass the scraped content along to the pipeline
    if content is not None:
      item = PageItem()
      item['wb_url'] = str(url.get_full_url())
      item['content'] = content
      item['site_id'] = getattr(self.site, 'id', None)
      yield item

    if self.stop_after_one:
      if len(next_urls) > 0:
        logging.info('Stopping after one, would have followed to:')
      else:
        logging.info('Stopping after one, no further links found')

    # Check each URL to see if we need to follow it
    relevant_next_wb_urls: List[WaybackUrl] = []
    for next_url in next_urls:
      next_wb_url = url.join(next_url)
      if self.is_relevant(next_wb_url):
        relevant_next_wb_urls.append(next_wb_url)

    # Provision rows
    if self.push:
      provision_empty_pages(get_connection(), self.site, relevant_next_wb_urls)

    # Follow each relevant URL
    for next_wb_url in relevant_next_wb_urls:
      if self.stop_after_one:
        logging.info(f'\t{next_wb_url.get_full_url()}')
      else:
        yield response.follow(next_wb_url.get_full_url(), self.parse)

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

  def handle_pdf(self, response: HtmlResponse) -> Tuple[Optional[str], List[str]]:
    # TODO see https://github.com/MrDiggles2/cru-scrape/issues/1
    logging.info(f'{response.url} is a PDF, skipping...')

    return ('', [])

  def is_relevant(self, link: WaybackUrl):

    logging.debug(f'Checking relevance of {link.get_full_url()}')

    # Check that we're staying on the page where we started

    if not link.contains(self.site.base_url):
      logging.debug(f'\tDoes not contain start URL')
      return False

    # Check that the year on the link is within one year of our start URL

    if self.year is not None and not link.matches_year(self.year, plus_minus = 1):
      logging.debug(f'\tDoes not match year')
      return False

    if link.get_original_url() in self.visited:
      logging.debug(f'\tAlready visited a previous snapshot')
      return False

    self.visited.add(link.get_original_url())

    logging.debug(f'\tGood')

    return True
