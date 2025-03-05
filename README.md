
# 🌟 InternDataSpider 🌟  
**高效聚合多平台实习/校招信息，助力求职者一键筛选心仪岗位！**  
[![GitHub Stars](https://img.shields.io/github/stars/niny9/InternDataSpider?style=social)](https://github.com/niny9/InternDataSpider)  
---

## 🚀 项目简介  
本项目是一个**面向特定实习信息的分布式爬虫系统**，专注于抓取并整合主流招聘平台（牛客网、Boss直聘、小红书）的实习、校招、社招信息。通过动态反爬策略、多源异构数据解析、弹性存储架构，实现高效数据采集与实时检索，帮助用户快速获取精准岗位信息！  

**核心功能亮点**：  
- 🔥 分布式爬虫：基于Scrapy-Redis实现高并发任务调度  
- 🛡️ 智能反爬：动态IP池、UA轮换、Selenium模拟操作  
- 📊 混合存储：MySQL + Elasticsearch + Logstash增量同步  
- 📈 实时监控：Prometheus + Grafana可视化运维  
- 🖥️ 交互界面：Bootstrap动态表单 + RESTful API  

---

## 🛠️ 技术栈  
| 模块                | 技术组件                                                                 |  
|---------------------|--------------------------------------------------------------------------|  
| **爬虫框架**         | Scrapy、Selenium、DrissionPage                                          |  
| **分布式调度**       | Redis Streams、RabbitMQ                                                 |  
| **数据存储**         | MySQL、Elasticsearch、Logstash                                         |  
| **运维监控**         | Prometheus、Grafana、Loki                                              |  
| **前端交互**         | HTML/CSS/JS、Bootstrap、jQuery                                         |  
| **部署工具**         | Docker、Kubernetes                                                      |  

---

## 📂 代码框架  
```bash  
InternDataSpider/  
├── crawlers/  
│   ├── zhipin_spider/           # Boss直聘爬虫（反爬策略+动态渲染）  
│   ├── xiaohongshu_spider1/     # 小红书笔记爬虫（异步接口监听）  
│   └── nowcode_one/             # 牛客网爬虫（标准化页面解析）  
│  
├── storage-docker/              # 存储服务Docker配置（MySQL+ES+Logstash）  
├── monitor/                     # Prometheus监控配置 + Grafana仪表盘  
├── frontend/                    # 前端交互页面（Bootstrap动态表单）  
│  
├── scripts/  
│   ├── 推送脚本.py              # URL去重与Redis任务分发  
│   ├── 小红书测试脚本.py        # 小红书反爬模拟测试  
│   └── 所有网址.txt            # 初始爬取URL集合  
│  
├── requirements.txt            # Python依赖库列表  
└── README.md                   # 项目文档（你正在看的这个！）  
```  

---

## 🚨 快速启动  

### 1️⃣ 安装依赖  
```bash  
pip install -r requirements.txt  
```  

### 2️⃣ WebDriver配置（Selenium必需）  
1. 访问 **[Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)** 下载与本地Chrome版本匹配的驱动  
2. 解压后找到 `chromedriver.exe`，将其复制到 **Python解释器所在目录**（如 `C:\Python39\Scripts\`）  

### 3️⃣ Redis服务部署  
1. **安装教程**：参考 [CSDN-Redis安装指南](https://blog.csdn.net/Leewayah/article/details/129427599)  
2. **启动服务**：  
   ```bash  
   # 双击 redis-server.exe 启动服务  
   # 在Redis目录打开CMD，输入以下命令：  
   redis-server  
   # 新开终端连接Redis  
   redis-cli  
   ```  

### 4️⃣ 运行爬虫  
```bash  
# Boss直聘爬虫（分片流式抓取）  
scrapy crawl zhipin --set REDIS_HOST=localhost  

# 手动添加初始URL到Redis队列  
lpush zhipin:start_urls "https://www.zhipin.com/web/geek/job?query=大数据&city=101020100"  
```  
📌 **URL分页技巧**：观察页码规律，如 `page=2` 至 `page=9`，依次添加至队列即可  

---

## ⚠️ 注意事项  
1. **路径问题**：  
   - 代理文件 `proxies.txt` 需放在项目根目录  
   - 确保 `webdriver.exe` 与Python解释器在同一路径  

2. **页面加载**：  
   - Boss直聘页面依赖特定标签加载（如 `.job-list-box`），若页面结构更新需调整XPath解析规则  
   - 小红书动态内容需定期维护 `DrissionPage` 的异步接口监听逻辑  

3. **反爬策略**：  
   - 代理IP可能不稳定，建议使用付费代理服务提升成功率  
   - 高频请求可能触发验证码，需结合请求频率控制和验证码识别方案  

---

## 🌈 贡献与支持  
🤝 **欢迎贡献**：  
- 提交PR优化反爬策略或解析逻辑  
- 补充新数据源适配（如拉勾网、智联招聘）  

🐞 **问题反馈**：  
在 [Issues](https://github.com/niny9/InternDataSpider/issues) 中描述问题，附上日志和复现步骤！  

---

**✨ 让求职不再信息过载，一键直达心仪Offer！**  
![招聘系统架构图](https://media.giphy.com/media/L1R1tvI9svkIWwpVYr/giphy.gif)  
```
