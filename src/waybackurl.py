from typing import List
import urllib.parse
import datetime
import re

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
    pathDate = urllib.parse.urlparse(self.url).path.split('/')[2]
    year = int(pathDate[0:4])
    month = int(pathDate[4:6])
    day = int(pathDate[6:8])

    return datetime.datetime(year, month, day)

  def from_url(url: str):
    no_port_url = re.sub(r':\d+/', '/', url)
    corrected_proto_url = re.sub(r'http://?', 'http://', no_port_url)
    return WaybackUrl(corrected_proto_url)
