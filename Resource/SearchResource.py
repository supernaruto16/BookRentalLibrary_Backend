from flask_restplus import Namespace, Resource, reqparse
from Utils.InputValidation import *
import html


api = Namespace('search')


search_parse = reqparse.RequestParser()
search_parse.add_argument('mode', type=str, choices=('title', 'author', 'isbn'), required=True, default='title')
search_parse.add_argument('text', type=str, default='')
search_parse.add_argument('limit', type=int, default=5)
search_parse.add_argument('page', type=int, default=1)


class Search(Resource):
    @api.expect(search_parse)
    def post(self):
        data = search_parse.parse_args()
        data['text'] = html.escape(data['text'])
        response = dict()
        response['data'] = list()

        if data['mode'] == 'title':
            books_details = BookDetails.search_by_title(data['text'], data['limit'], data['page'])
            response['data'] = [each.as_dict() for each in books_details]
            return response, 200
        elif data['mode'] == 'isbn':
            books_details = BookDetails.search_by_isbn(data['text'], data['limit'], data['page'])
            response['data'] = [each.as_dict() for each in books_details]
            return response, 200
        elif data['mode'] == 'author':
            authors_details = AuthorDetails.search_by_name(data['text'], data['limit'], data['page'])
            response['data'] = [each.as_dict() for each in authors_details]
            return response, 200
