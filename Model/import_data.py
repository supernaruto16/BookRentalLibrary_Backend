from Model.models import *
import json
import os


ratings_json_path = os.getcwd() + '/Model/data/ratings.json'
book_categories_json_path = os.getcwd() + '/Model/data/book_categories.json'
books_json_path = os.getcwd() + '/Model/data/books13.json'
authors_json_path = os.getcwd() + '/Model/data/authors.json'
categories_json_path = os.getcwd() + '/Model/data/categories.json'


def import_data():
    with open(authors_json_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            data = json.loads(line)
            author = AuthorDetails(author_name=data['name'],
                                   author_id=data['id'])
            author.save_to_db()

    with open(books_json_path) as f:
        lines = f.readlines()
        total = len(lines)
        for line in lines:
            data = json.loads(line)
            book = BookDetails(ISBN=data['isbn13'],
                               book_title=data['title'],
                               publication_year=data['original_publication_year'],
                               book_description=data['description'],
                               author_id=data['author_id'],
                               book_cover=data['image_url'])
            book.save_to_db()

    with open(categories_json_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            data = json.loads(line)
            category = CategoryDetails(category_id=data['id'],
                                       category_name=data['name'])
            category.save_to_db()

    with open(book_categories_json_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            data = json.loads(line)
            for category_id in data['categories_id']:
                book_category = BookCategories(book_id=data['isbn'],
                                               category_id=category_id)
                book_category.save_to_db()

    with open(ratings_json_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            data = json.loads(line)
            rating_detail = RatingDetails(user_id=data['user_id'],
                                          book_id=data['isbn13'],
                                          rating_num=data['rating'])
            rating_detail.save_to_db()
