# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhipinSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class JobItem(scrapy.Item):
    position = scrapy.Field()      # 职位名称
    company = scrapy.Field()        # 公司名称
    salary = scrapy.Field()         # 薪资范围
    city = scrapy.Field()       # 工作地点
    experience = scrapy.Field()     # 经验要求
    degree = scrapy.Field()      # 学历要求
    jobType = scrapy.Field()  
    job_url = scrapy.Field()        # 职位链接 (推荐作为唯一标识)
    companySize = scrapy.Field()   # 公司规模
