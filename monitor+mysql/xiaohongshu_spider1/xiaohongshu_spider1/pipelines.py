# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
from scrapy.exceptions import DropItem
import json

class XiaohongshuSpider1Pipeline:
    def process_item(self, item, spider):
        return item

class MySQLPipeline:
    def __init__(self, mysql_host, mysql_port, mysql_db, mysql_user, mysql_password, mysql_charset):
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_db = mysql_db
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_charset = mysql_charset

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_port=crawler.settings.get('MYSQL_PORT'),
            mysql_db=crawler.settings.get('MYSQL_DB'),
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD'),
            mysql_charset=crawler.settings.get('MYSQL_CHARSET')
        )

    def open_spider(self, spider):
        # 连接数据库
        self.conn = pymysql.connect(
            host=self.mysql_host,
            port=self.mysql_port,
            user=self.mysql_user,
            password=self.mysql_password,
            db=self.mysql_db,
            charset=self.mysql_charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        # 关闭连接
        self.conn.close()

    def process_item(self, item, spider):
        # 数据清洗
        adapter = ItemAdapter(item)
        if not adapter.get('note_id'):
            raise DropItem("Missing note_id in %s" % item)

        # 构建 SQL
        sql = """
        INSERT INTO xiaohongshu (note_id, title, author, user_id, likes, cover_url, image_urls)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            title = VALUES(title),
            likes = VALUES(likes),
            image_urls = VALUES(image_urls)
        """
        try:
            self.cursor.execute(sql, (
                adapter['note_id'],
                adapter['title'],
                adapter['author'],
                adapter['user_id'],
                adapter['likes'],
                adapter['cover_url'],
                json.dumps(adapter['image_urls'])  # 列表转 JSON 字符串
            ))
            self.conn.commit()
            
        except pymysql.Error as e:
            self.conn.rollback()
            spider.logger.error("MySQL Error: %s" % str(e))
        return item