from flask_restplus import Namespace, Resource, reqparse
from Model.models import CategoryDetails


api = Namespace('categories')

all_req = reqparse.RequestParser()
all_req.add_argument('limit', type=int, default=10)
all_req.add_argument('page', type=int, default=1)


class AllCategory(Resource):
    @api.expect(all_req)
    def get(self):
        data = all_req.parse_args()
        all_categories = CategoryDetails.return_all(data['limit'], data['page'])

        return all_categories


popular_parse = reqparse.RequestParser()
popular_parse.add_argument('limit', type=int, default=10)
popular_parse.add_argument('page', type=int, default=1)


class PopularCategories(Resource):
    @api.expect(popular_parse)
    def get(self):
        data = popular_parse.parse_args()
        popular = {
            'data': list(map(lambda x: {
                'category_id': x[1],
                'category_name': x[2],
                'num_books': x[0]
            }, CategoryDetails.popular_categories(int(data['limit']), int(data['page']))))
        }
        return popular
