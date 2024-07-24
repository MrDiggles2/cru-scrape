import scrapy
import re
import urllib.parse
import logging
from item import MyItem
from bs4 import BeautifulSoup
from bs4.element import Comment

def normalize_link(url: str, originUrl: str):
  # remove any mailto urls
  if url.find('mailto:') > -1:
    return None

  # i.e. #first-level-nav
  if url.startswith('#'):
    return None

  joined_url = url
  # i.e. hunting_trapping/hunting/MainesGamePlanForDeer.htm
  if not url.startswith('http'):
    joined_url = urllib.parse.urljoin(originUrl, url)

  no_port_url = re.sub(r':\d+/', '/', joined_url)
  corrected_proto_url = re.sub(r'http://?', 'http://', no_port_url)
  return corrected_proto_url

def text_from_html(rawHtml: str):

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
  wayback_url: str

  def __init__(self, start_url, *args, **kwargs):
    super().__init__(*args, **kwargs)
    logging.getLogger('scrapy').setLevel(logging.WARNING)

    self.start_urls.append(start_url)

    wayback_path = urllib.parse.urlparse(start_url).path
    domain_index = wayback_path.find('http')
    self.wayback_url = normalize_link('', wayback_path[domain_index:])
    self.year = wayback_path.split('/')[2][0:4]

  def parse(self, response):

    url = normalize_link('', response.request.url)

    print(f'at {url}')

    item = MyItem()
    item['url'] = str(url)
    item['content'] = str(text_from_html(response.body))
    item['original_date'] = str(response.headers.get('X-Archive-Orig-Date'))

    yield item

    for href in response.css('a::attr(href)'):
        n_link = normalize_link(str(href), url)
        if n_link is None:
          print(f'skipping 1 {n_link}')
          continue

        if not self.is_relevant(n_link):
          continue

        yield response.follow(n_link, self.parse)

  def is_relevant(self, link: str):

    logging.info(f'Checking relevance of {link}')

    # Check that we're staying on the page where we started

    if link.find(self.wayback_url) == -1:
      logging.info(f'\tDoes not contain {self.wayback_url}')
      return False

    # Check that the year on the link matches where we started

    year = urllib.parse.urlparse(link).path.split('/')[2][0:4]
    if not self.year == year:
      logging.info(f'\tDoes not match year {self.year}')
      return False

    logging.info(f'\tgood')

    return True
