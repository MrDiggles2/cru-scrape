import scrapy

class MyItem(scrapy.Item): 
  url = scrapy.Field()
  content = scrapy.Field()
  original_date = scrapy.Field()
