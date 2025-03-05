from elasticsearch import Elasticsearch

SIZE = 100

# 连接配置（根据实际环境修改）
es = Elasticsearch(
    hosts=["localhost:9200"],  # Elasticsearch地址。本地用"localhost:9200"，docker内用"es容器名:9200"
    timeout=30,  # 超时时间
)

zhipin_columns = ["position", "company", "salary", "city", "experience", "degree", "companySize","jobType", "job_url"]
newcode_columns = ["position", "salary", "company", "company_industry", "company_scale", "description", "working_days", "duration", "page_type"]
xiaohongshu_columns = ["note_id", "title", "author", "user_id", "likes", "cover_url", "image_urls"]
    
def query_zhipin_any(index_name, index_columns, position, company, city):
    try:
        query_body = {"query": {
                                "bool":{
                                    "must": [
                                        {"wildcard": {"position.keyword": "*"+ position+ "*"}},
                                        {"wildcard": {"company.keyword": "*"+ company+ "*"}},
                                        {"wildcard": {"city.keyword": "*"+ city+ "*"}},
                                    ]
                                },          
                     },
                     "size": SIZE
        }

        #  执行查询
        response = es.search(
            index=index_name,  # 指定单索引
            body=query_body
            )
        
        # 解析结果
        results = []
        for hit in response["hits"]["hits"]:
            item = {}
            item["id"] = hit["_id"]
            for i in index_columns:
                item[i] = hit["_source"][i]
            results.append(item)
        
        return results
    
    except Exception as e:
        print(f"Elasticsearch查询错误: {str(e)}")
        return []

def query_newcode_any(index_name, index_columns, position, company, description):
    try:
        query_body = {"query": {
                                "bool":{
                                    "must": [
                                        {"wildcard": {"position.keyword": "*"+ position+ "*"}},
                                        {"wildcard": {"company.keyword": "*"+ company+ "*"}},
                                        {"wildcard": {"description.keyword": "*"+ description+ "*"}},
                                    ]
                                },          
                     },
                     "size": SIZE
        }
    
        #  执行查询
        response = es.search(
            index=index_name,  # 指定单索引
            body=query_body
            )
        
        # 解析结果
        results = []
        for hit in response["hits"]["hits"]:
            item = {}
            item["id"] = hit["_id"]
            for i in index_columns:
                item[i] = hit["_source"][i]
            results.append(item)
        return results
    
    except Exception as e:
        print(f"Elasticsearch查询错误: {str(e)}")
        return []
    
def query_xiaohongshu_any(index_name, index_columns, position, city, company ):
    try:
        query_body = {"query": {
                                "bool":{
                                    "must": [
                                        {"wildcard": {"title.keyword": "*"+ position+ "*"}},
                                        {"wildcard": {"title.keyword": "*"+ city+ "*"}},
                                        {"wildcard": {"title.keyword": "*"+ company+ "*"}},
                                        # {"wildcard": {"title.keyword": "*"+ title+ "*"}}
                                    ]
                                },          
                     },
                     "size": SIZE
        }

        #  执行查询
        response = es.search(
            index=index_name,  # 指定单索引
            body=query_body
            )
        
        # 解析结果
        results = []
        for hit in response["hits"]["hits"]:
            item = {}
            item["id"] = hit["_id"]
            for i in index_columns:
                item[i] = hit["_source"][i]
            results.append(item) 
        return results
    
    except Exception as e:
        print(f"Elasticsearch查询错误: {str(e)}")
        return []

def main():
    print("欢迎使用职位查询系统！")
    while True:
        # 获取用户输入
        position = input("请输入职位名称(可选)：").strip()
        city = input("请输入城市（可选）：").strip()
        company = input("请输入公司名称（可选）：").strip()       
        
        # 查询职位信息
        results_zhipin = query_zhipin_any("zhipin_table", zhipin_columns, position = position, city = city, company = company)
        results_new_code = query_newcode_any("newcode_crawler", newcode_columns, position = position, company = company, description = city)
        results_xiaohongshu = query_xiaohongshu_any("xiaohongshu_table", xiaohongshu_columns, position = position, city = city, company = company)
        
        # 输出结果
        if results_zhipin or results_new_code or results_xiaohongshu:
            print("\n查找到以下职位信息：")
            if results_zhipin:
                print("\n======================来源: Boss直聘======================\n")
                for i in range(len(results_zhipin)):
                    job = results_zhipin[i]
                    print(f"{i}.职位名称: 【{job['position']}】;",
                    f"公司名称: {job['company']};",
                    f"城市: {job['city']};",
                    f"薪资: {job['salary']};",
                    f"工作经验要求: {job['experience']};",
                    f"学历要求: {job['degree']};",
                    f"公司规模: {job['companySize']};",
                    f"岗位类型: {job['jobType']};",
                    f"岗位链接: {job['job_url']}")
            if results_new_code:
                print("\n======================来源: 牛客网======================\n")
                for i in range(len(results_new_code)):
                    job  = results_new_code[i]
                    print(f"{i}.职位名称:【{job['position']}】;",
                    f"公司名称: {job['company']};", 
                    f"岗位描述: {job['description']};",
                    f"薪资: {job['salary']};", 
                    f"公司规模: {job['company_scale']};",
                    f"岗位类型: {job['page_type']};",
                    f"岗位要求工作时长: {job['duration']}, {job['working_days']}")
            if results_xiaohongshu:
                print("\n======================来源: 小红书======================\n")
                for i in range(len(results_xiaohongshu)):
                    job = results_xiaohongshu[i]
                    print(f"{i}.标题: 【{job['title']}】;", 
                    f"作者: {job['author']};", 
                    f"点赞数: {job['likes']};", 
                    f"内容链接: {job['cover_url']}")

        else:
            print("\n未找到符合条件的职位信息。")
        
        # 询问是否继续查询
        continue_search = input("\n是否继续查询？（y/n）：").strip().lower()
        if continue_search != 'y':
            print("感谢使用职位查询系统，再见！")
            break

if __name__ == "__main__":
    main()
