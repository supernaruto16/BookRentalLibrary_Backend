from flask_restplus import Namespace, Resource, reqparse
from Model.models import AuthorDetails


api = Namespace('authors')

top_parse = reqparse.RequestParser()
top_parse.add_argument('limit', type=int, default=5)
top_parse.add_argument('page', type=int, default=1)


class TopAuthor(Resource):
    @api.expect(top_parse)
    def get(self):
        data = top_parse.parse_args()
        return AuthorDetails.return_top(int(data['limit']), int(data['page']))
