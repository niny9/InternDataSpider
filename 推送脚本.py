import redis

# 连接 Redis
redis_client = redis.StrictRedis(host='172.20.10.2', port=6379, decode_responses=True)

# 定义分片的 Redis Streams
sharded_urls = {
    "zhipin_stream_1": [
        "https://www.zhipin.com/web/geek/job?query=%E5%A4%A7%E6%95%B0%E6%8D%AE%E6%9A%91%E6%9C%9F%E5%AE%9E%E4%B9%A0&city=101020100&experience=108&degree=203&scale=306&page=1",
        "https://www.zhipin.com/web/geek/job?query=%E5%A4%A7%E6%95%B0%E6%8D%AE%E6%9A%91%E6%9C%9F%E5%AE%9E%E4%B9%A0&city=101020100&experience=108&degree=203&scale=306&page=2",
        "https://www.zhipin.com/web/geek/job?query=%E5%A4%A7%E6%95%B0%E6%8D%AE%E6%9A%91%E6%9C%9F%E5%AE%9E%E4%B9%A0&city=101020100&experience=108&degree=203&scale=306&page=3",
        "https://www.zhipin.com/web/geek/job?query=%E5%A4%A7%E6%95%B0%E6%8D%AE%E6%9A%91%E6%9C%9F%E5%AE%9E%E4%B9%A0&city=101020100&experience=108&degree=203&scale=306&page=4",
        "https://www.zhipin.com/web/geek/job?query=%E5%A4%A7%E6%95%B0%E6%8D%AE%E6%9A%91%E6%9C%9F%E5%AE%9E%E4%B9%A0&city=101020100&experience=108&degree=203&scale=306&page=5"
    ],
    "zhipin_stream_2": [
        "https://www.zhipin.com/web/geek/job?query=%E5%A4%A7%E6%95%B0%E6%8D%AE%E6%9A%91%E6%9C%9F%E5%AE%9E%E4%B9%A0&city=101020100&experience=108&degree=203&scale=306&page=6",
        "https://www.zhipin.com/web/geek/job?query=%E5%A4%A7%E6%95%B0%E6%8D%AE%E6%9A%91%E6%9C%9F%E5%AE%9E%E4%B9%A0&city=101020100&experience=108&degree=203&scale=306&page=7",
        "https://www.zhipin.com/web/geek/job?query=%E5%A4%A7%E6%95%B0%E6%8D%AE%E6%9A%91%E6%9C%9F%E5%AE%9E%E4%B9%A0&city=101020100&experience=108&degree=203&scale=306&page=8",
        "https://www.zhipin.com/web/geek/job?query=%E5%A4%A7%E6%95%B0%E6%8D%AE%E6%9A%91%E6%9C%9F%E5%AE%9E%E4%B9%A0&city=101020100&experience=108&degree=203&scale=306&page=9",
        "https://www.zhipin.com/web/geek/job?query=%E5%A4%A7%E6%95%B0%E6%8D%AE%E6%9A%91%E6%9C%9F%E5%AE%9E%E4%B9%A0&city=101020100&experience=108&degree=203&scale=306&page=10"
    ]

}

for stream, urls in sharded_urls.items():
    for url in urls:
        redis_client.xadd(stream, {"url": url})


QUEUE_NAME1 = "nowcoder:start_urls"
QUEUE_NAME2 = "xiaohongshu:start_urls"

URL_SET = "visited_urls"  # 存储已爬取的 URL
redis_client.delete(URL_SET)
def push_task(url):
    """添加 URL 任务，并检查是否已爬取"""
    if not redis_client.sismember(URL_SET, url):  # URL 不存在
        redis_client.sadd(URL_SET, url)  # 添加到已爬取列表
        if "nowcoder" in url:
            redis_client.lpush(QUEUE_NAME1, url)  # 加入任务队列
        if "xiaohongshu" in url:
            redis_client.lpush(QUEUE_NAME2, url)  # 加入任务队列
    else:
        print(f"任务已存在，跳过: {url}")

with open("F:/monitor+mysql/所有网址.txt", "r") as f:
    for i in f:
        push_task(i)

# 将 URL 推送到不同的 Stream


