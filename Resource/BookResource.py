from flask_restplus import Namespace, Resource, reqparse
from Model.models import BookDetails, BookWarehouse, UserDetails
from flask_jwt_extended import jwt_required
import html
from Utils.InputValidation import *

api = Namespace('books')

newbook_parse = reqparse.RequestParser()
newbook_parse.add_argument('limit', type=int, default=5)
newbook_parse.add_argument('page', type=int, default=1)


class NewBook(Resource):
    @api.expect(newbook_parse)
    def get(self):
        data = newbook_parse.parse_args()

        new_book = {
            'data': list(map(lambda x: {
                'ISBN': x.ISBN,
                'book_title': x.book_title,
                'publication_year': x.publication_year,
                'book_description': x.book_description,
                'book_cover': x.book_cover,
                'author': x.author_details.author_name
            },
                             BookDetails.return_new(int(data['limit']), int(data['page']))))
        }
        return new_book


category_books_parse = reqparse.RequestParser()
category_books_parse.add_argument('category_id', type=int, required=True)
category_books_parse.add_argument('limit', type=int, default=10)
category_books_parse.add_argument('page', type=int, default=1)


class AllBooksByCategory(Resource):
    @api.expect(category_books_parse)
    def get(self):
        data = category_books_parse.parse_args()

        books = {
            'data': list(map(lambda x: {
                'ISBN': x.ISBN,
                'book_title': x.book_title,
                'publication_year': x.publication_year,
                'book_description': x.book_description,
                'book_cover': x.book_cover,
                'author': x.author_details.author_name
            },
                             BookDetails.return_by_category(int(data['category_id']), int(data['limit']),
                                                            int(data['page']))))
        }
        return books


top_parse = reqparse.RequestParser()
top_parse.add_argument('limit', type=int, default=10)
top_parse.add_argument('page', type=int, default=1)


class TopBooks(Resource):
    @api.expect(top_parse)
    def get(self):
        data = top_parse.parse_args()

        books = {
            'data': list(map(lambda x: {
                'ISBN': x.ISBN,
                'book_title': x.book_title,
                'publication_year': x.publication_year,
                'book_description': x.book_description,
                'book_cover': x.book_cover,
                'rating': list(map(lambda rating_ele: rating_ele.rating_num, x.ratings_details))
            },
                             BookDetails.return_top_books(int(data['limit']),
                                                          int(data['page']))))
        }
        return books
        # return BookDetails.return_top_books(int(data['limit']), int(data['page']))


details_parse = reqparse.RequestParser()
details_parse.add_argument('book_id', required=True)


class DetailsBook(Resource):
    @api.expect(details_parse)
    def get(self):
        data = details_parse.parse_args()
        v = BookDetails.get_book_details(data['book_id'])
        if not v[0]:
            return 'Book does not exist', 400
        book_details = v[1]
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}


        books = {
            'data': list(map(lambda x: {
                'ISBN': x.ISBN,
                'book_title': x.book_title,
                'publication_year': x.publication_year,
                'book_description': x.book_description,
                'book_cover': x.book_cover,
                'rating': list(map(lambda rating_ele: rating_ele.rating_num, x.ratings_details)),
                'author': {
                    'author_name': x.author_details.author_name,
                    'author_id': x.author_details.author_id
                }
            },
                            book_details))
        }
        return books, 200
        # return row2dict(book_details), 200


ratings_parse = reqparse.RequestParser()
ratings_parse.add_argument('book_id', required=True)
ratings_parse.add_argument('limit', type=int, default=5)
ratings_parse.add_argument('page', type=int, default=1)


class RatingsBook(Resource):
    @api.expect(ratings_parse)
    def get(self):
        data = ratings_parse.parse_args()
        res = dict()
        res['data'] = []
        v = validate_book_id(data['book_id'])
        if not v[0]:
            return 'Book does not exist', 400
        book_details = v[1]
        rating_details = RatingDetails.find_by_book(book_details.ISBN, data['limit'], data['page'])
        for each_rating in rating_details:
            each_res = dict()
            each_res['rating_num'] = each_rating['rating_num']
            each_res['rating_comment'] = each_rating['rating_comment']
            each_res['email'] = UserDetails.find_by_id(each_rating['user_id']).email
            res['data'].append(each_res)
        return res, 200
