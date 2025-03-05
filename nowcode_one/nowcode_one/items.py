# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NowcodeOneItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class JobItem(scrapy.Item):
    position = scrapy.Field()
    salary = scrapy.Field()
    company = scrapy.Field()
    company_industry = scrapy.Field()
    company_scale = scrapy.Field()
    description = scrapy.Field()
    working_days = scrapy.Field()
    duration = scrapy.Field()
    location = scrapy.Field()
    page_type = scrapy.Field()