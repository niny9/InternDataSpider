# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class XiaohongshuSpider1Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NoteItem(scrapy.Item):
    note_id = scrapy.Field()     # 笔记ID
    title = scrapy.Field()       # 标题
    author = scrapy.Field()      # 作者名
    user_id = scrapy.Field()     # 用户ID
    likes = scrapy.Field()       # 点赞数
    cover_url = scrapy.Field()   # 封面图URL
    image_urls = scrapy.Field()  # 图片URL列表
