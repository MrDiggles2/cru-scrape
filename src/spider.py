import scrapy
from scrapy.http import Response
from bs4 import BeautifulSoup
from bs4.element import Comment
import logging
import re

from src.entities import Site, PageItem
from src.waybackurl import WaybackUrl
from src.utils.url import sanitize_url

def text_from_html(rawHtml: str):

  # TODO: Handle PDFs

  soup = BeautifulSoup(rawHtml, 'html.parser')

  # Remove wayback machine elements

  def decomposeIfExists(element):
    if element:
      element.decompose()

  decomposeIfExists(soup.find('div', id='wm-ipp-base'))
  decomposeIfExists(soup.find('div', id='wm-ipp-print'))

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
  return re.sub(r'\s+', ' ', joined_text).strip()

class Spider(scrapy.Spider):
  name = 'spider'
  site = Site
  start_urls = []
  start_wayback_url: WaybackUrl
  visited = set()
  on_first_page = True
  base_url: str

  def __init__(self, wb_url: str, site: Site, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.site = site
    self.start_wayback_url = WaybackUrl.from_url(wb_url)

    # This is how scrapy knows where to scrape
    self.start_urls.append(wb_url)

    # Always suppress scrapy logs
    logging.getLogger('scrapy').setLevel(logging.ERROR)
    

  def parse(self, response: Response):
    url = WaybackUrl.from_url(response.request.url)

    print(self.on_first_page)

    if self.on_first_page:
      self.base_url = sanitize_url(url.get_original_url())
      self.on_first_page = False

    logging.info(f'at {url.get_full_url()}')

    item = PageItem()
    item['wb_url'] = str(url.get_full_url())
    item['content'] = str(text_from_html(response.body))
    item['site_id'] = self.site.id

    # We need to check here since WB will occasionally redirect to a different
    # year. If we encounter those, we should just ignore it to avoid muddling up
    # the data.
    if url.matches_year(self.start_wayback_url):
      yield item

    for href in response.css('a::attr(href)'):
        n_link = url.join(str(href))

        if self.is_relevant(n_link):
          yield response.follow(n_link.get_full_url(), self.parse)

  def is_relevant(self, link: WaybackUrl):

    logging.debug(f'Checking relevance of {link.get_full_url()}')

    # Check that we're staying on the page where we started

    if not link.contains(self.base_url):
      logging.debug(f'\tDoes not contain start URL')
      return False

    # Check that the year on the link matches where we started

    if not self.start_wayback_url.matches_year(link):
      logging.debug(f'\tDoes not match year')
      return False

    if link.get_original_url() in self.visited:
      logging.debug(f'\tAlready visited a previous snapshot')
      return False

    self.visited.add(link.get_original_url())

    logging.debug(f'\tGood')

    return True
