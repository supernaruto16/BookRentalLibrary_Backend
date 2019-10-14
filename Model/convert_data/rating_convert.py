import csv
import json
import os


csv_ratings_path = os.getcwd() + '/../ratings.csv'
json_ratings_path = os.getcwd() + '/ratings.json'
json_books_path = os.getcwd() + '/books13.json'

id_to_ISBN = {}
with open(json_books_path, 'r') as f:
    lines = f.readlines()
    for data in lines:
        data = json.loads(data)
        book_id = int(data['id'])
        isbn13 = data['isbn13']
        id_to_ISBN[str(book_id)] = str(isbn13)

data = []
with open(csv_ratings_path, 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        book_id = int(row['book_id'])
        if str(book_id) not in id_to_ISBN:
            continue
        row['isbn13'] = id_to_ISBN[str(book_id)]
        data.append(row)

with open(json_ratings_path, 'w+') as f:
    for row in data:
        print(row['isbn13'])
        f.write('%s\n' % (json.dumps(row)))

