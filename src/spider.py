import scrapy
import logging
from item import MyItem
from bs4 import BeautifulSoup
from bs4.element import Comment
from waybackurl import WaybackUrl
from logger import logger

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

  return u" ".join(t.strip() for t in visible_texts)

class Spider(scrapy.Spider):
  name = 'spider'
  start_urls = []
  start_wayback_url: WaybackUrl
  visited = set()

  def __init__(self, start_url, *args, **kwargs):
    super().__init__(*args, **kwargs)
    logging.getLogger('scrapy').setLevel(logging.WARNING)

    root = logging.getLogger()
    if root.handlers:
      for handler in root.handlers:
          root.removeHandler(handler)

    self.start_urls.append(start_url)
    self.start_wayback_url = WaybackUrl.from_url(start_url)

  def parse(self, response):
    url = WaybackUrl.from_url(response.request.url)

    logger.info(f'at {url.get_full_url()}')

    item = MyItem()
    item['url'] = str(url.get_full_url())
    item['base_url'] = str(self.start_wayback_url.get_original_url())
    item['content'] = str(text_from_html(response.body))

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

    logger.info(f'Checking relevance of {link.get_full_url()}')

    # Check that we're staying on the page where we started

    if not link.matches_origin(self.start_wayback_url):
      logger.info(f'\tDoes not contain start URL')
      return False

    # Check that the year on the link matches where we started

    if not self.start_wayback_url.matches_year(link):
      logger.info(f'\tDoes not match year')
      return False

    if link.get_original_url() in self.visited:
      logger.info(f'\tAlready visited a previous snapshot')
      return False

    self.visited.add(link.get_original_url())

    logger.info(f'\tGood')

    return True
