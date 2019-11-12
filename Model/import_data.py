from Model.models import *
import json
import os


class ImportData:
    def __init__(self, data_path):
        self.book_details = None
        self.ratings_json_path = data_path + '/ratings.json'
        self.book_categories_json_path = data_path + '/book_categories.json'
        self.books_json_path = data_path + '/books13.json'
        self.authors_json_path = data_path + '/authors.json'
        self.categories_json_path = data_path + '/categories.json'

    def import_authors(self):
        with open(self.authors_json_path, 'r') as f:
            lines = f.readlines()
            total = len(lines)
            for i in range(len(lines)):
                data = json.loads(lines[i])
                print(f'[+] author [{i+1}/{total}]')
                author = AuthorDetails(author_name=data['name'],
                                       author_id=data['id'])
                author.save_to_db()

    def import_books(self):
        with open(self.books_json_path) as f:
            lines = f.readlines()
            total = len(lines)
            for i in range(len(lines)):
                data = json.loads(lines[i])
                print(f'[+] book [{i+1}/{total}]')
                publication_year = data['publication_year']
                if publication_year is None:
                    publication_year = data['original_publication_year']

                book = BookDetails(ISBN=data['isbn13'],
                                   book_title=data['title'],
                                   publication_year=publication_year,
                                   book_description=data['description'],
                                   author_id=data['author_id'],
                                   book_cover=data['image_url'])
                book.save_to_db()

    def import_categories(self):
        with open(self.categories_json_path, 'r') as f:
            lines = f.readlines()
            total = len(lines)
            for i in range(len(lines)):
                data = json.loads(lines[i])
                print(f'[+] category [{i+1}/{total}]')
                category = CategoryDetails(category_id=data['id'],
                                           category_name=data['name'])
                category.save_to_db()

    def import_book_categories(self):
        with open(self.book_categories_json_path, 'r') as f:
            lines = f.readlines()
            total = len(lines)
            self.book_details = BookDetails()
            for i in range(len(lines)):
                data = json.loads(lines[i])
                print(f"[+] book_category [{i+1} / {total}]")
                for category_id in data['categories_id']:
                    book_id = data['isbn']
                    if self.book_details.find_by_isbn(book_id):
                        book_category = BookCategories(book_id=data['isbn'],
                                                       category_id=category_id)
                        book_category.save_to_db()

    # with open(ratings_json_path, 'r') as f:
    #     lines = f.readlines()
    #     total = len(lines)
    #     book_details = BookDetails()
    #     for i in range(len(lines)):
    #         data = json.loads(lines[i])
    #         print(f'[+] rating [{i+1}/{total}]')
    #         rating_detail = RatingDetails(user_id=data['user_id'],
    #                                       book_id=data['isbn13'],
    #                                       rating_num=data['rating'])
    #         rating_detail.save_to_db()
