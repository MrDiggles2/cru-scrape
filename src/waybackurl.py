import logging
import urllib.parse
import datetime
import re

from src.utils.url import remove_protocol_and_www, sanitize_url

class WaybackUrl:
  url: str

  def __init__(self, url: str):
    self.url = url

  def is_valid(self):
    result = re.match(r'^https?:\/\/web.archive.org\/web\/', self.url)
    return False if result is None else True

  def get_full_url(self):
    return self.url

  def is_pdf(self):
    return self.get_original_url().lower().endswith('.pdf')
  
  def get_original_url(self):
    wayback_path = urllib.parse.urlparse(self.url).path
    domain_index = wayback_path.find('http')
    return wayback_path[domain_index:]

  def get_snapshot_date(self):

    pattern = r'\b\d{14}\b'
    matches = re.findall(pattern, self.get_full_url())
    pathDate = ''
    if matches and matches[0]:
      pathDate = matches[0]

    year = int(pathDate[0:4]) if pathDate[0:4] else 1
    month = int(pathDate[4:6]) if pathDate[4:6] else 1
    day = int(pathDate[6:8]) if pathDate[6:8] else 1

    return datetime.datetime(year, month, day)

  def from_url(url: str):
    no_port_url = re.sub(r':\d+/', '/', url)
    corrected_proto_url = re.sub(r'http://?', 'http://', no_port_url)
    no_anchor_url = corrected_proto_url.split("#")[0]

    return WaybackUrl(no_anchor_url)

  def matches_year(self, year: int, plus_minus = 0):
    logging.debug(f'\tchecking year')
    logging.debug(f'\t\t{year}')
    logging.debug(f'\t\t{self.get_snapshot_date().year}')
    return abs(self.get_snapshot_date().year - year) <= plus_minus

  def join(self, path: str):
    joined_url = path
    # i.e. hunting_trapping/hunting/MainesGamePlanForDeer.htm
    if not path.startswith('http'):
      joined_url = urllib.parse.urljoin(self.get_full_url(), path)

    return WaybackUrl.from_url(joined_url)

  def contains(self, url: str):
    me = remove_protocol_and_www(self.get_original_url())
    them = remove_protocol_and_www(url)

    logging.debug(f'\tchecking origin')
    logging.debug(f'\t\t{me}')
    logging.debug(f'\t\t{them}')

    return  me.find(them) > -1
