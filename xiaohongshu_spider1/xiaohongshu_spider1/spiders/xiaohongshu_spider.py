from scrapy_redis.spiders import RedisSpider
from DrissionPage import WebPage
from time import sleep, time
import random
import json
from .data_parser import parse_note_data, save_to_json  # 导入解析函数
# from .data_storage import data_storage
from ..items import NoteItem
from prometheus_client import Counter, Histogram, Gauge, start_http_server

class XiaohongshuSpider1CrawlSpider(RedisSpider):
    name = "xiaohongshu_spider"
    redis_key = 'xiaohongshu:start_urls'

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.wp = WebPage()

        # 初始化普罗米修斯指标
        self.pages_crawled = Counter('pages_crawled_total', 'Total number of pages crawled')
        # 用于统计已爬取的页面总数
        self.requests_total = Counter('requests_total', 'Total number of requests made')
        # 用于统计总共发起的请求数量
        self.request_failures = Counter('request_failures_total', 'Total number of request failures')
        # 用于统计请求失败的总次数
        self.request_latency = Histogram('request_latency_seconds', 'Request latency in seconds')
        # 用于记录请求的延迟时间（以秒为单位）
        self.crawl_speed = Gauge('crawl_speed_pages_per_second', 'Crawling speed in pages per second')  # 新增爬虫速度指标
        # 用于实时监控爬虫的爬取速度（每秒爬取的页面数）
         
        # 启动普罗米修斯HTTP服务器
        start_http_server(8000)  # 在8000端口上暴露指标

        # 加载代理池
        proxy_path = "F:/monitor+mysql/xiaohongshu_spider1/proxies.txt"
        with open(proxy_path, 'r') as f:
            self.proxies = [line.strip() for line in f if line.strip()]

        # 加载请求头
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        ]
        self.user_agents = user_agents

        # 初始化爬虫速度相关变量
        self.start_time = time()  # 记录爬虫启动时间
        self.total_pages_crawled = 0  # 记录总爬取页面数

    def process_request(self, request, spider):
        # 随机选择代理
        proxy = random.choice(self.proxies)
        request.meta['proxy'] = proxy

        # 随机选择请求头
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent

    def parse(self, response, **kwargs):
        self.requests_total.inc()  # 增加请求总数
        start_time = time()

        try:
            self.wp.get("https://www.xiaohongshu.com")
            self.wp.wait.load_start()

            sleep(5)

            # 在搜索框中输入关键词并搜索暑期实习
            search_input = self.wp.ele('#search-input')
            search_input.input('上海暑期实习')
            self.wp.ele('.search-icon').click()

            sleep(2)
            self.wp.refresh()
            self.wp.listen.start('web/v1/search/notes')
            pk = self.wp.listen.wait()
            pkbody = pk.response.body

            if isinstance(pkbody, dict):
                raw_data = pkbody
            else:
                raw_data = json.loads(pkbody)

            # 实时解析数据
            parsed_data = parse_note_data(raw_data)  # 使用解析函数
            
            # 数据存储到mysql中
            for item in parsed_data:
                note = NoteItem()
                for field in note.fields:
                    note[field] = item[field]
                yield note
            
            save_to_json(parsed_data, 'xiaohongshu_data.json')  # 保存解析结果

            self.pages_crawled.inc()  # 增加爬取页面数量
            self.total_pages_crawled += 1  # 更新总爬取页面数

            # 计算爬虫速度
            elapsed_time = time() - self.start_time
            if elapsed_time > 0:
                speed = self.total_pages_crawled / elapsed_time  # 计算每秒处理的页面数
                self.crawl_speed.set(speed)  # 更新爬虫速度指标

        except Exception as e:
            self.request_failures.inc()  # 增加请求失败数
            print(f"请求失败: {str(e)}")

        finally:
            latency = time() - start_time
            self.request_latency.observe(latency)  # 记录请求延迟时间
# lpush xiaohongshu:start_urls https://www.xiaohongshu.com
# scrapy crawl xiaohongshu_spider

# 要下载个DrissionPage库 
