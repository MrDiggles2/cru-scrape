import scrapy

class Site():

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

class PageItem(scrapy.Item): 
  wb_url = scrapy.Field()
  content = scrapy.Field()
  site_id = scrapy.Field()

