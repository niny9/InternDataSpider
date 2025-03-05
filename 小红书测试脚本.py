import redis
import subprocess

def test_url_management():
    # 1. 连接到Redis
    try:
        r = redis.Redis(host='172.20.10.2', port=6379, db=0)
        print("Redis连接成功:", r.ping())
    except Exception as e:
        print("Redis连接失败:", str(e))
        return

    # 2. 清空队列并推送起始URL
    try:
        r.delete('xiaohongshu:start_urls')
        r.lpush('xiaohongshu:start_urls', 'https://www.xiaohongshu.com')
        print("URL推送成功，当前队列长度:", r.llen('xiaohongshu:start_urls'))
    except Exception as e:
        print("Redis操作失败:", str(e))
        return

    # 3. 启动爬虫（指定项目路径）
    try:
        process = subprocess.Popen(
            ['scrapy', 'crawl', 'xiaohongshu_spider'],
            cwd='F:/monitor+mysql/xiaohongshu_spider1',  # 替换为实际路径
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        combined_output = stdout.decode('utf-8') + stderr.decode('utf-8')
        print("爬虫输出:\n", combined_output)  # 调试输出

        # 4. 检查关键日志（调整断言关键词）
        assert 'Crawled (200)' in combined_output, "未找到爬取成功的日志"
        assert 'https://www.xiaohongshu.com' in combined_output, "未找到目标URL"
        print("测试通过!")
    except Exception as e:
        print("测试失败:", str(e))

# 执行测试
test_url_management()