import json
import os
import xmltodict
import pprint

xml_books_folder = os.getcwd() + '/../books_xml/books_xml/'
json_books_path = os.getcwd() + '/books13.json'
json_authors_path = os.getcwd() + '/authors.json'
category_details_path = os.getcwd() + '/book_categories.json'

export_book_filter = ['id', 'isbn13', 'title', 'image_url', 'average_rating', 'description', 'publication_year']
export_book_work_filter = ['original_publication_year', 'original_title', 'rating_dist']
export_author_filter = ['id', 'name']
export_book_data = []
export_author_data = []
category_details = {}
normalize_id = {}

with open(category_details_path, 'r') as f:
    lines = f.readlines()
    for line in lines:
        data = json.loads(line)
        category_details[data['isbn']] = data['categories_id']
        
def process_rating_dist(rating_dist):
    res = {}
    for dist in rating_dist.split('|'):
        star, num = dist.split(':')
        res[str(star)] = num
    return res

cnt_author = 0
def get_normalize_author_id(base_id):
    global cnt_author
    if base_id not in normalize_id:
        cnt_author += 1
        normalize_id[base_id] = cnt_author
    return normalize_id[base_id]

pp = pprint.PrettyPrinter(indent=4)
for filename in os.listdir(xml_books_folder):
    # print filename,
    with open(xml_books_folder + filename, 'r') as xml_file:
        xmldata = xmltodict.parse(xml_file)
        bookdata = xmldata['GoodreadsResponse']['book']
        res_book = {}
        res_author = {}
        for field in export_book_filter:
            res_book[str(field)] = bookdata[str(field)]
        for field in export_book_work_filter:
            res_book[str(field)] = bookdata['work'][str(field)]

        if not res_book['isbn13'] or len(res_book['isbn13']) <= 0:
            continue
        
        # print res_book['original_publication_year']
        if isinstance(res_book['original_publication_year'], dict):
            if '#text' in res_book['original_publication_year']:
                res_book['original_publication_year'] = res_book['original_publication_year']['#text']
            else:
                continue
        # print res_book['original_publication_year'],

        if res_book['rating_dist']:
            res_book['rating_dist'] = process_rating_dist(res_book['rating_dist'])

        for field in export_author_filter:
            if isinstance(bookdata['authors']['author'], list):
                res_author[str(field)] = bookdata['authors']['author'][0][str(field)]
            else:
                res_author[str(field)] = bookdata['authors']['author'][str(field)]
        res_author['id'] = get_normalize_author_id(res_author['id'])
        res_book['author_id'] = res_author['id']
        
        res_book['id'] = bookdata['work']['id']
        if isinstance(res_book['id'], dict):
            if '#text' in res_book['id']:
                res_book['id'] = res_book['id']['#text']

        res_book['categories'] = category_details[res_book['isbn13']]

        # print res_book['id']
        # pp.pprint(export_author_data)
        # pp.pprint(bookdata['authors']['author'][0])
        export_book_data.append(res_book)
        export_author_data.append(res_author)
        # break

 
with open(json_books_path, 'w') as f:
    for row in export_book_data:
        f.write('%s\n' % json.dumps(row))

printed_id = []
with open(json_authors_path, 'w') as f:
    for row in export_author_data:
        if row['id'] in printed_id:
            continue
        printed_id.append(row['id'])
        f.write('%s\n' % json.dumps(row))