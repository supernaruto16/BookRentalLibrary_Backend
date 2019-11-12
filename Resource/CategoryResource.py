from flask_restplus import reqparse, Resource

from Model.models import CategoryDetails


class AllCategory(Resource):
    def get(self):
        all_categories = CategoryDetails.return_all()
        return all_categories


popular_parse = reqparse.RequestParser()
popular_parse.add_argument('limit', default=10)
popular_parse.add_argument('page', default=1)


class PopularCategories(Resource):
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
