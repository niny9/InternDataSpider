from ..items import JobItem 

def data_storage(parsed_data):


    item = JobItem()
    for field in item.fields:
        item[field] = parsed_data.get(field)
        print("llll:",item[field])

    return item
