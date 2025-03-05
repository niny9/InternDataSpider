pip install -r requirements.txt

一些注意事项
1.webdriver的下载可以打开这个网址：https://googlechromelabs.github.io/chrome-for-testing/
下载完成会有一个压缩文件，需要将其解压后的webdriver.exe文件放到和电脑本地的python.exe解释器一个文件夹中

2.redis服务器可以参考csdn网址https://blog.csdn.net/Leewayah/article/details/129427599?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522da15965bb636d62b4a8427b3ad1f2667%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=da15965bb636d62b4a8427b3ad1f2667&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-129427599-null-null.142^v101^pc_search_result_base7&utm_term=redis%E4%B8%8B%E8%BD%BD&spm=1018.2226.3001.4187的教程

3.配置好之后的操作
a.在下载好的redis文件夹中 双击redis-server.exe文件打开
b.在该文件夹鼠标右键空白 打开cmd终端 输入指令 redis-server 这样就打开redis了
c.在终端中继续输入redis-cli 准备输入redis指令了
d.scrapy crawl zhipin 这个指令在vscode的终端输入就可以了 
e.lpush zhipin:start_urls https://www.zhipin.com/web/geek/job?query=%E5%A4%A7%E6%95%B0%E6%8D%AE&city=101020100
//这个网址就是boss直聘大数据的一些岗位 它一共有九页 可以看看页码的规律 再继续输入不同的网址就行 

最后注意代码里的一些文件路径问题 例如代理 还有页面加载根据一个特定的标签出现为止 这个标签可能换页面就没了（但在域名 也就是https://www.zhipin.com开头的网址应该没问题）


