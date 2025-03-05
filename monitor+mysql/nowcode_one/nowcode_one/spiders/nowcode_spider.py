import json
from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from urllib.parse import urljoin
import random
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from .data_parser import parse_page  # 导入解析模块
from .data_storage import data_storage # 导入存储模块
from prometheus_client import start_http_server, Counter, Gauge, Summary


# 启动普罗米修斯监控服务器
start_http_server(8001)

# 定义普罗米修斯指标
REQUEST_TOTAL = Counter('spider_requests_total', 'Total number of requests made by the spider')
# 用于统计爬虫总共发起的请求数量
PARSE_SUCCESS = Counter('spider_parse_success_total', 'Total number of successfully parsed pages')
# 用于统计爬虫成功解析的页面总数
REQUEST_FAILURE = Counter('spider_request_failures_total', 'Total number of failed requests')
# 用于统计爬虫请求失败的总次数
REQUEST_LATENCY = Summary('spider_request_latency_seconds', 'Request latency in seconds')
# 用于记录爬虫请求的延迟时间（以秒为单位），Summary 类型会计算分位数（如 P50, P90, P99）
CRAWL_SPEED = Gauge('spider_crawl_speed_pages_per_second', 'Crawling speed in pages per second')  # 新增爬虫速度指标
# 用于实时监控爬虫的爬取速度（每秒爬取的页面数），Gauge 类型表示一个可以上下浮动的值

class NowcodeSpiderSpider(RedisSpider):
    name = "nowcode_spider"
    allowed_domains = ["nowcoder.com"]
    redis_key = 'nowcoder:start_urls'

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

        # 加载代理池
        proxy_path = "D:\\Desktop\\monitor\\nowcode_one\\proxies.txt"  # 替换为您的代理池文件路径
        with open(proxy_path, 'r') as f:
            self.proxies = [line.strip() for line in f if line.strip()]

        # 加载请求头
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.127 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.127 Safari/537.36',
            # 添加更多请求头
        ]

        self.user_agent = random.choice(self.user_agents)
        self.chrome_options = Options()
        self.chrome_options.add_argument(f'user-agent={self.user_agent}')

        # 启动浏览器
        self.driver = webdriver.Chrome(options=self.chrome_options)

        # 初始化爬虫速度相关变量
        self.start_time = time.time()  # 记录爬虫启动时间
        self.total_pages_crawled = 0  # 记录总爬取页面数

    def process_request(self, request, spider):
        # 随机选择代理
        proxy = random.choice(self.proxies)
        request.meta['proxy'] = proxy

        # 随机选择请求头
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent

    def parse(self, response):
        REQUEST_TOTAL.inc()  # 增加请求总数
        start_time = time.time()
        time.sleep(2)
        self.driver.get(response.url)

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "el-pager")))
        time.sleep(1)
        page_source = self.driver.page_source

        # 识别页面类型
        page_type = self.get_page_type(response.url)

        # 调用解析模块
        try:
            parsed_data = parse_page(page_type, page_source)
            PARSE_SUCCESS.inc()  # 增加成功解析的页面数量
            self.total_pages_crawled += 1  # 更新总爬取页面数

            # 计算爬虫速度
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                speed = self.total_pages_crawled / elapsed_time  # 计算每秒处理的页面数
                CRAWL_SPEED.set(speed)  # 更新爬虫速度指标

        except Exception as e:
            REQUEST_FAILURE.inc()  # 增加失败的请求数量
            self.logger.error(f"Failed to parse page: {e}")
            return
        finally:
            end_time = time.time()  # 记录请求结束时间
            latency = end_time - start_time  # 计算延迟时间
            REQUEST_LATENCY.observe(latency)

        # 将解析后的数据传递给下一个处理阶段
        for job in parsed_data:
            job['page_type'] = page_type
            # 存储到mysql中
            item = data_storage(job)
            yield item
            yield job

        # 保存解析的内容为json文件
        # json_filename = f'{page_type}_jobs.json'
        # with open(json_filename, 'w', encoding='utf-8') as json_file:
        #     json.dump(parsed_data, json_file, ensure_ascii=False, indent=4)

    def get_page_type(self, url):
        if '/jobs/school/jobs' in url:
            return 'school_recruitment'  # 校招
        elif '/jobs/intern/center' in url:
            return 'intern_recruitment'  # 实习
        elif '/jobs/fulltime/center' in url:
            return 'fulltime_recruitment'  # 社招
        else:
            return 'unknown'

# scrapy crawl nowcode_spider
# lpush nowcoder:start_urls https://www.nowcoder.com/jobs/intern/center?recruitType=2&city=%E4%B8%8A%E6%B5%B7&careerJob=11029
# lpush nowcoder:start_urls https://www.nowcoder.com/jobs/intern/center?recruitType=2&page=2&city=%E4%B8%8A%E6%B5%B7&careerJob=11029
# lpush nowcoder:start_urls https://www.nowcoder.com/jobs/intern/center?recruitType=2&page=3&city=%E4%B8%8A%E6%B5%B7&careerJob=11029
