import json
import os


base_category_details_path = os.getcwd() + '/base_category_details.json'
category_details_path= os.getcwd() + '/category_details.json'
categories_path = os.getcwd() + '/categories.json'

base_data = {}
category_details = []
categories = {}
categories_list = []

with open(base_category_details_path, 'r') as f:
    base_data = json.loads(f.read())

id = 0
for key in base_data:
    detail = {'isbn': key, 'categories': base_data[key], 'categories_id': []}
    for category in base_data[key]:
        if category not in categories:
            categories[category] = id + 1
            id += 1
            categories_list.append({'name': category, 'id': id})
        detail['categories_id'].append(categories[category])
    category_details.append(detail)

with open(categories_path, 'w') as f:
    for data in categories_list:
        f.write('%s\n' % json.dumps(data))

with open(category_details_path, 'w') as f:
    for data in category_details:
        f.write('%s\n' % json.dumps(data))