from flask_restplus import Namespace, Resource, reqparse
from Model.models import BookDetails, BookWarehouse, UserDetails
from flask_jwt_extended import jwt_required
import html


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
details_parse.add_argument('id', required=True)


class DetailsBook(Resource):
    @api.expect(details_parse)
    def get(self):
        data = details_parse.parse_args()
        book_details = BookDetails.find_by_isbn(html.escape(data['id']))
        if not book_details:
            return 'Book does not exist', 400
        book_warehouses = book_details.book_warehouse
        if not book_warehouses:
            return book_details, 200
        warehouses_info = list()
        for each in book_warehouses:
            owner_details = UserDetails.find_by_id(each.owner_id)
            warehouses_info.append((owner_details.email, each.price, each.warehouse_id))
        return {
            'book': book_details.as_dict(),
            'warehouses': warehouses_info
        }, 200
