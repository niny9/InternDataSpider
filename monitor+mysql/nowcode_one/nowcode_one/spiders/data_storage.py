from ..items import JobItem 

def data_storage(data):
    item = JobItem()
    # data = job.meta['data']
    # 映射JSON字段到Item
    for field in item.fields:
        if field in data:
            print(data[field])
            item[field] = data.get(field)
    return item
