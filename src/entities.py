from typing import Optional
import scrapy

class Site():

  id = str
  base_url = str
  start_url = str
  organization_id = str
  start_year = int
  end_year = int

  def __init__(self, psql_dict):
    self.id = psql_dict['id']
    self.start_url = psql_dict['start_url']
    self.base_url = psql_dict['base_url']
    self.organization_id = psql_dict['organization_id']
    self.start_year = psql_dict['start_year']
    self.end_year = psql_dict['end_year']


  def to_dict(self):
    return {
      'id': self.id,
      'base_url': self.base_url,
      'start_url': self.start_url,
      'organization_id': self.organization_id,
      'start_year': self.start_year,
      'end_year': self.end_year,
    }

class StartPage():
  id: Optional[str]
  wb_url: str

  def __init__(self, psql_dict):
    self.id = psql_dict['id']
    self.wb_url = psql_dict['wb_url']

class PageItem(scrapy.Item):
  # This will be set if a row is already provisioned for this page
  page_id = scrapy.Field()
  wb_url = scrapy.Field()
  content = scrapy.Field()
  site_id = scrapy.Field()

  def to_dict(self):
    return {
      'page_id': self['page_id'],
      'wb_url': self['wb_url'],
      'content': self['content'],
      'site_id': self['site_id']
    }
