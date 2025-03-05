# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
from twisted.enterprise import adbapi


class NowcodeOnePipeline:
    def process_item(self, item, spider):
        return item

class MySQLAsyncPipeline:
    def __init__(self, db_config):
        # 初始化数据库连接池
        self.dbpool = adbapi.ConnectionPool(
            'pymysql',
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            db=db_config['database'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    @classmethod
    def from_crawler(cls, crawler):
        # 从 settings.py 加载配置
        db_config = {
            'host': crawler.settings.get('MYSQL_HOST'),
            'user': crawler.settings.get('MYSQL_USER'),
            'password': crawler.settings.get('MYSQL_PASSWORD'),
            'database': crawler.settings.get('MYSQL_DB')
        }
        return cls(db_config)

    def process_item(self, item, spider):
        # 异步插入数据
        query = self.dbpool.runInteraction(
            self._insert_record,
            item
        )
        query.addErrback(self._handle_error, item)
        return item

    def _insert_record(self, tx, item):
        # 数据清洗逻辑
        # adapter = ItemAdapter(item)
        cleaned_data = {
            'position': item.get('position', ''),
            'salary': item.get('salary', ''),
            'company': item.get('company', ''),
            'company_industry': item.get('company_industry', ''),
            'company_scale': item.get('company_scale', ''),
            'description': item.get('description', ''),
            'working_days': item.get('working_days', ''),
            'duration': item.get('duration', ''),
            'page_type': item.get('page_type', 'intern_recruitment'),
            # 'location': self.extract_location(item.get('description')),

        }

        sql = """
            INSERT INTO newcode_crawler 
            (position, salary, company, company_industry, company_scale, 
            description, working_days, duration, page_type)
            VALUES ( 
            %(position)s, %(salary)s, %(company)s, %(company_industry)s,
            %(company_scale)s, %(description)s, %(working_days)s, %(duration)s, 
            %(page_type)s
            )
            """
      
        tx.execute(sql, cleaned_data)
    
    def _handle_error(self, failure, item, spider):
        # 错误处理
        spider.logger.error(f"数据库操作失败: {failure.value} | 数据: {dict(item)}")

    def close_spider(self, spider):
        # 关闭连接池
        self.dbpool.close()
