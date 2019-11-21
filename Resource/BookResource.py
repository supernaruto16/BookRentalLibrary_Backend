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
        return BookDetails.return_top_books(int(data['limit']), int(data['page']))


details_parse = reqparse.RequestParser()
details_parse.add_argument('book_id', required=True)


class DetailsBook(Resource):
    @api.expect(details_parse)
    def get(self):
        data = details_parse.parse_args()
        v = validate_book_id(data['book_id'])
        if not v[0]:
            return 'Book does not exist', 400
        book_details = v[1]
        return book_details.as_dict(), 200


ratings_parse = reqparse.RequestParser()
ratings_parse.add_argument('book_id', required=True)


class RatingsBook(Resource):
    @api.expect(ratings_parse)
    def get(self):
        data = details_parse.parse_args()
        v = validate_book_id(data['book_id'])
        if not v[0]:
            return 'Book does not exist', 400
        book_details = v[1]
        return RatingDetails.find_by_book(book_details.book_id, data['limit'], data['page']), 200
