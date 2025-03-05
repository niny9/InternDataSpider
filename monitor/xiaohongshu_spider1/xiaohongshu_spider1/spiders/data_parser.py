import json
from typing import List, Dict
from prometheus_client import Counter

# 初始化普罗米修斯指标
data_parsed_total = Counter('data_parsed_total', 'Total number of data parsed')
data_parse_failures = Counter('data_parse_failures_total', 'Total number of data parse failures')

def parse_note_data(raw_data: dict) -> List[Dict]:
    """解析小红书笔记数据"""
    results = []
    items = raw_data.get('data', {}).get('items', [])
    for item in items:
        try:
            if item.get('model_type') != 'note':
                continue

            note_card = item.get('note_card', {})
            user_info = note_card.get('user', {})
            interact_info = note_card.get('interact_info', {})
            cover_info = note_card.get('cover', {})

            # 提取图片URL（优先取WB_DFT类型）
            image_urls = []
            for img in note_card.get('image_list', []):
                for info in img.get('info_list', []):
                    if info.get('image_scene') == 'WB_DFT':
                        image_urls.append(info.get('url'))
                        break  # 每个图片只取一个默认URL

            parsed = {
                'note_id': item.get('id'),
                'title': note_card.get('display_title'),
                'author': user_info.get('nickname'),
                'user_id': user_info.get('user_id'),
                'likes': int(interact_info.get('liked_count', 0)),
                'cover_url': cover_info.get('url_default'),
                'image_urls': image_urls,
                'timestamp': item.get('time')  # 根据实际数据结构调整
            }
            results.append(parsed)
            data_parsed_total.inc()  # 增加解析成功数

        except Exception as e:
            data_parse_failures.inc()  # 增加解析失败数
            print(f"解析失败: {str(e)}")

    return results

def save_to_json(data: List[Dict], filename: str):
    """保存解析结果到JSON文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"成功保存 {len(data)} 条数据到 {filename}")
    except Exception as e:
        print(f"保存文件失败: {str(e)}")
