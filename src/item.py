import scrapy

class MyItem(scrapy.Item): 
  url = scrapy.Field()
  content = scrapy.Field()
  base_url = scrapy.Field()
