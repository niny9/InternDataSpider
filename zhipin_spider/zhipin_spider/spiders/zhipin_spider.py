import scrapy
from scrapy_redis.spiders import RedisSpider
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import redis
from .data_parser import NewDataParser
from .data_storage import data_storage
from prometheus_client import start_http_server, Counter, Gauge, Summary
import time

# 普罗米修斯监控指标

# REQUESTS_TOTAL: 用于记录爬虫发出的总请求数
# 指标名称: zhipin_requests_total
# 指标描述: Total number of requests made
REQUESTS_TOTAL = Counter('zhipin_requests_total', 'Total number of requests made')
# PAGES_CRAWLED: 用于记录爬虫成功爬取的总页面数
# 指标名称: zhipin_pages_crawled
# 指标描述: Total number of pages crawled
PAGES_CRAWLED = Counter('zhipin_pages_crawled', 'Total number of pages crawled')
# REQUESTS_FAILED: 用于记录爬虫失败的请求数
# 指标名称: zhipin_requests_failed
# 指标描述: Total number of failed requests
REQUESTS_FAILED = Counter('zhipin_requests_failed', 'Total number of failed requests')
# REQUEST_LATENCY: 用于记录每个请求的延迟（从发出请求到收到响应的时间）
# 指标名称: zhipin_request_latency_seconds
# 指标描述: Request latency in seconds
# Summary 类型会记录延迟的分布情况（如平均值、分位数等）
REQUEST_LATENCY = Summary('zhipin_request_latency_seconds', 'Request latency in seconds')
# CRAWL_SPEED: 用于记录爬虫的爬取速度（每秒处理的页面数）
# 指标名称: zhipin_crawl_speed_pages_per_second
# 指标描述: Crawling speed in pages per second
# Gauge 类型表示瞬时值，适合记录当前的速度
CRAWL_SPEED = Gauge('zhipin_crawl_speed_pages_per_second', 'Crawling speed in pages per second')

class ZhipinSpider(RedisSpider):
    name = 'zhipin'
    redis_stream = "zhipin_stream_2"

    def __init__(self, *args, **kwargs):
        super(ZhipinSpider, self).__init__(*args, **kwargs)
        start_http_server(8000)  # 启动prometheus HTTP服务器

        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 禁用自动化检测
        chrome_options.add_argument("--disable-extensions")  # 禁用扩展

        self.driver = webdriver.Chrome(options=chrome_options)

        # 加载代理池 代理池路径注意下 
        proxy_path = "F:/monitor+mysql/zhipin_spider/proxies.txt"  # 替换为您的代理池文件路径
        try:
            with open(proxy_path, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"代理池文件 {proxy_path} 未找到，将不使用代理。")
            self.proxies = []

        # 加载请求头 注意把请求头里面的 Chrome版本号 （我的浏览器版本是133.0.6943.127） 和自己电脑的匹配上即可 
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.142 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.142 Safari/537.36',
            # 添加更多请求头
        ]
        self.user_agents = user_agents

        # 初始化数据解析器
        self.parser = NewDataParser()

        # 初始化爬虫速度相关变量
        self.start_time = time.time()
        self.pages_crawled = 0

    def start_requests(self):
        """ 从 Redis Stream 获取 URL 并生成请求 """
        redis_client = redis.StrictRedis(host='172.20.10.2', port=6379, decode_responses=True)

        # 读取 Stream 数据 (最多获取 20 条)
        messages = redis_client.xread({self.redis_stream: "0"}, count=20, block=10000)  

       
        # 解析 Redis Streams 数据
        for stream, entries in messages:
            for entry_id, entry_data in entries:
                url = entry_data.get("url")  # 获取 URL
                print(url)
                if url:
                    yield scrapy.Request(url=url, callback=self.parse)

    def process_request(self, request, spider):
        if self.proxies:
            # 随机选择代理
            proxy = random.choice(self.proxies)
            request.meta['proxy'] = proxy

        # 随机选择请求头
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent

    def parse(self, response):
        start_time = time.time()
        REQUESTS_TOTAL.inc()
        try:
            self.driver.get(response.url)
            job_list_box = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-list-box"))
                )
            job_elements = job_list_box.find_elements(By.CSS_SELECTOR, '.job-card-wrapper')
            for job in job_elements:
                parsed_data = self.parser.parse(job)
                # 存储到mysql
                item = data_storage(parsed_data)
                yield item
            PAGES_CRAWLED.inc()
            self.pages_crawled += 1

            # 计算爬虫速度
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                crawl_speed = self.pages_crawled / elapsed_time
                CRAWL_SPEED.set(crawl_speed)

            print("Job data has been parsed and stored.")
        except Exception as e:
            REQUESTS_FAILED.inc()
            print(f"An error occurred: {e}")
        finally:
            # 记录请求延迟
            REQUEST_LATENCY.observe(time.time() - start_time)


# scrapy crawl zhipin

# docker run -d --name mysql_container -e MYSQL_ROOT_PASSWORD=123456 -p 3306:3306 mysql:latest
# docker exec -it mysql_container /bin/bash
# docker run -it --rm redis redis-cli -h 172.20.10.2 -p 6379
# mysql -u root -p
# create database crawler_storage;

# SET NAMES 'utf8mb4';   
#    USE crawler_storage;
   
# CREATE TABLE `zhipin_table` (
# `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '唯一标识',
# `position` VARCHAR(255) NOT NULL COMMENT '职位名称',
# `company` VARCHAR(255)  DEFAULT NULL COMMENT '公司名称',
# `city` VARCHAR(100) NOT NULL COMMENT '所在城市',
# `experience` VARCHAR(50) DEFAULT NULL COMMENT '经验要求（如：1-3年）',
# `degree` VARCHAR(50) DEFAULT NULL COMMENT '学历要求（如：本科及以上）',
# `salary` VARCHAR(50) DEFAULT NULL COMMENT '薪资范围（如：8k-15k）',
# `companySize` VARCHAR(50) DEFAULT NULL COMMENT '公司规模（如：10000人以上）',
# `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间：自动生成，与爬取时间对应',
# `source` VARCHAR(50) DEFAULT NULL COMMENT '爬取来源：牛客/小红书等',
# `jobType` VARCHAR(50) DEFAULT NULL COMMENT '职位类型：实习/春招等',
# `job_url` VARCHAR(50) DEFAULT NULL COMMENT 'url'
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='职位信息表';
# select * from zhipin_table