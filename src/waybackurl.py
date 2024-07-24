from typing import List
import urllib.parse
import datetime
import re

import logging

class WaybackUrl:
  url: str

  def __init__(self, url: str):
    self.url = url

  def get_full_url(self):
    return self.url
  
  def get_original_url(self):
    wayback_path = urllib.parse.urlparse(self.url).path
    domain_index = wayback_path.find('http')
    return wayback_path[domain_index:]

  def get_snapshot_date(self):
    group = re.match(r'/(\d{14})/', self.get_full_url())
    pathDate = ''
    if group and group.group(0):
      pathDate = group.group(0)

    year = int(pathDate[0:4]) if pathDate[0:4] else 1
    month = int(pathDate[4:6]) if pathDate[4:6] else 1
    day = int(pathDate[6:8]) if pathDate[6:8] else 1

    return datetime.datetime(year, month, day)

  def from_url(url: str):
    no_port_url = re.sub(r':\d+/', '/', url)
    corrected_proto_url = re.sub(r'http://?', 'http://', no_port_url)
    return WaybackUrl(corrected_proto_url)

  def matches_origin(self, parent: "WaybackUrl"):
    logging.debug(f'\tchecking origin')
    logging.info(f'\t\t{parent.get_full_url()}')
    logging.info(f'\t\t{self.get_full_url()}')
    return self.get_original_url().find(parent.get_original_url()) > -1

  def matches_year(self, url: "WaybackUrl"):
    logging.debug(f'\tchecking year')
    logging.info(f'\t\t{url.get_snapshot_date().year()}')
    logging.info(f'\t\t{self.get_snapshot_date().year}')
    return self.get_snapshot_date().year == url.get_snapshot_date().year

  def join(self, path: str):
    joined_url = path
    # i.e. hunting_trapping/hunting/MainesGamePlanForDeer.htm
    if not path.startswith('http'):
      joined_url = urllib.parse.urljoin(self.get_full_url(), path)

    return WaybackUrl.from_url(joined_url)
