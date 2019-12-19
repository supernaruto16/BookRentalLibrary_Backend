from Model.models import *
import json
from urllib.parse import urlparse
import os


class ImportData:
    def __init__(self, data_path):
        self.book_details = None
        self.ratings_json_path = data_path + '/ratings.json'
        self.book_categories_json_path = data_path + '/book_categories.json'
        self.books_json_path = data_path + '/books13.json'
        self.authors_json_path = data_path + '/authors.json'
        self.categories_json_path = data_path + '/categories.json'
        self.num_rand_user = 60000

    def import_user_type(self):
        types = []
        types.append(UserTypeDetails(user_type_name='admin'))
        types.append(UserTypeDetails(user_type_name='user'))
        types.append(UserTypeDetails(user_type_name='validator'))
        for each in types:
            print(each.user_type_id)
            each.save_to_db()

    def import_authors(self):
        with open(self.authors_json_path, 'r') as f:
            lines = f.readlines()
            total = len(lines)
            for i in range(len(lines)):
                data = json.loads(lines[i])
                print(f'[+] author [{i + 1}/{total}]')
                author = AuthorDetails(author_name=data['name'],
                                       author_id=data['id'])
                author.save_to_db()

    def import_books(self):
        with open(self.books_json_path) as f:
            lines = f.readlines()
            total = len(lines)
            for i in range(len(lines)):
                data = json.loads(lines[i])
                print(f'[+] book [{i + 1}/{total}]')
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

    @staticmethod
    def fix_book_image():
        for book in BookDetails.query.all():
            print(f'[+] Fix book: {book.ISBN}')
            size_idx = book.book_cover.rfind('/')
            large_cover_url = ''
            if "nophoto" in book.book_cover:
                large_cover_url = book.book_cover[:size_idx - 1] + 'k' + book.book_cover[size_idx:]
            else:
                large_cover_url = book.book_cover[:size_idx - 1] + 'l' + book.book_cover[size_idx:]
            book.book_cover = large_cover_url
            book.save_to_db(force=True)

    def import_categories(self):
        with open(self.categories_json_path, 'r') as f:
            lines = f.readlines()
            total = len(lines)
            for i in range(len(lines)):
                data = json.loads(lines[i])
                print(f'[+] category [{i + 1}/{total}]')
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
                print(f"[+] book_category [{i + 1} / {total}]")
                for category_id in data['categories_id']:
                    book_id = data['isbn']
                    if self.book_details.find_by_isbn(book_id):
                        book_category = BookCategories(book_id=data['isbn'],
                                                       category_id=category_id)
                        book_category.save_to_db()

    def import_user(self):
        for i in range(self.num_rand_user):
            user_details = UserDetails.find_by_id(i)
            if user_details:
                continue
            print(f'[+] user [{i + 1}/{self.num_rand_user}]')
            user_details = UserDetails(
                first_name='test' + str(i),
                last_name='test' + str(i),
                email='test' + str(i) + '@test.com',
                password=UserDetails.generate_hash('12345', ),
                cash=1000,
                user_type_id=1
            )
            user_details.save_to_db()

    def import_rating_books(self):
        with open(self.ratings_json_path, 'r') as f:
            lines = f.readlines()
            total = len(lines)
            for i in range(len(lines)):
                data = json.loads(lines[i])
                user_details = UserDetails.find_by_id(data['user_id'])
                rating_details = RatingDetails.find_existing(data['user_id'], data['isbn13'])
                book_details = BookDetails.find_by_isbn(data['isbn13'])
                if not book_details or not user_details or rating_details:
                    continue
                print(f'[+] rating [{i + 1}/{total}]')
                rating_detail = RatingDetails(user_id=data['user_id'],
                                              book_id=data['isbn13'],
                                              rating_num=data['rating'],
                                              rating_comment='Lorem ipsum dolor sit amet, consectetur adipiscing '
                                                             'elit. Sed venenatis risus ut lectus dapibus, '
                                                             'tincidunt tempor lectus faucibus. Integer varius '
                                                             'blandit libero eget hendrerit. Suspendisse est augue, '
                                                             'ullamcorper sed dolor et, accumsan semper lorem. Class '
                                                             'aptent taciti sociosqu ad litora torquent per conubia '
                                                             'nostra, per inceptos himenaeos. Curabitur accumsan '
                                                             'condimentum ex. Aliquam cursus enim rhoncus elit '
                                                             'fringilla interdum. Proin scelerisque nec elit a '
                                                             'cursus.')
                book_details.add_rating(data['rating'])
                rating_detail.save_to_db()
                book_details.save_to_db()
