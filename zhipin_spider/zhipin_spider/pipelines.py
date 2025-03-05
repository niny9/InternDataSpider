# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from twisted.enterprise import adbapi  # 异步操作支持
import pymysql

class ZhipinSpiderPipeline:
    def process_item(self, item, spider):
        return item

class MySQLPipeline:
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
        adapter = ItemAdapter(item)
        cleaned_data = {
            'position': adapter.get('position', ''),
            'company': adapter.get('company', ''),
            'salary': adapter.get('salary', '面议'),
            'city': adapter.get('city', '未知'),
            'experience': adapter.get('experience', '不限'),
            'degree': adapter.get('degree', '不限'),
            'companySize': adapter.get('companySize', '未知'),
            'jobType': adapter.get('jobType', ''),
            'job_url': adapter.get('job_url', ''),
        }

        # 执行 SQL
        sql = """
        INSERT INTO zhipin_table (
            position, company, salary, city, 
            experience, degree, companySize, jobType,
            job_url
        ) VALUES (
            %(position)s, %(company)s, %(salary)s, %(city)s,
            %(experience)s, %(degree)s, %(companySize)s, %(jobType)s, 
            %(job_url)s
        ) 
        """
        tx.execute(sql, cleaned_data)
    
    def _handle_error(self, failure, item, spider):
        # 错误处理
        spider.logger.error(f"数据库操作失败: {failure.value} | 数据: {dict(item)}")

    def close_spider(self, spider):
        # 关闭连接池
        self.dbpool.close()