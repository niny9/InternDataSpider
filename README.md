1. cmd进入该文件夹主目录，然后输入命令：docker-compose up -d。
2. （如果报错：Error response from daemon: Get "https://registry-1. docker. io/v2/": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)，可能是网络问题，可以多配置几个镜像源，参考https://blog.csdn.net/wenxuankeji/article/details/143783262）
3. 等待镜像拉取完成。
4. docker desktop中应该是这样的界面。logstash应该没有任何error。

![image-20250303215212357](README.assets/image-20250303215212357.png)

4. 然后结束了
5. 现在直接运行飞书里的monitor+sql里的爬虫，就可以把数据存到mysql中。mysql存储的同时，logstash的log中会看到新插入的数据，表示正在传输到es中。
6. 运行index.py或者run_query.sh（两个是一样的）（需要先pip install elasticsearch==7.11.0），进入查询命令，就可以从es中进行查询。

<img src="README.assets/image-20250303220025491.png" alt="image-20250303220025491" style="zoom:50%;" />