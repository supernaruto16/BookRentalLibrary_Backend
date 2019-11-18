from flask_restplus import Resource, reqparse
from Model.models import AuthorDetails

top_parse = reqparse.RequestParser()
top_parse.add_argument('limit', type=int, default=5)
top_parse.add_argument('page', type=int, default=1)


class TopAuthor(Resource):
    def get(self):
        data = top_parse.parse_args()
        return AuthorDetails.return_top(int(data['limit']), int(data['page']))
