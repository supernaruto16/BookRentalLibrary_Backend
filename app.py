from flask import Flask, jsonify, request, render_template
from flask_restplus import Resource, Api, fields, reqparse
from flask_cors import CORS
from DB_Connection.db import init, sql_db
from flask_jwt_extended import JWTManager
from Model.RevokedTokenModel import RevokedTokenModel
import json
from Resource import UserValidationResource, BookResource, CategoryResource, AuthorResource, WarehousesResource, \
    UserResource, SearchResource
from Model.import_data import ImportData
import os
from Model.models import UserDetails


def factory():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    CORS(app)
    return app


app = factory()

with open('./config.json') as json_data_file:
    data = json.load(json_data_file)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + data["user"] + ':' + data["password"] + '@localhost/' + \
                                        data["database"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

# app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# app.config['JWT_COOKIE_SECURE'] = False
# app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
# app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
# app.config['JWT_COOKIE_CSRF_PROTECT'] = True

init(app)
jwt = JWTManager(app)


# @app.route('/')
# def helloworld():
#     return "Hello"


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)


@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The {} token has expired'.format(token_type)
    }), 401


api = Api(app, version='1.0', title='BookRental API',
          description='BookRental API')
jwt._set_error_handler_callbacks(api)

auth_ns = api.namespace('auth', description='Authentication API')
# admin_ns = api.namespace('admin', description='Admin API')
books_ns = api.namespace('books', description='Books API')
authors_ns = api.namespace('authors', description='Authors API')
categories_ns = api.namespace('categories', description='Categories API')
search_ns = api.namespace('search', description='Search API')
user_ns = api.namespace('user', description='User API')
warehouses_ns = api.namespace('warehouses', description='Warehouses API')

db = sql_db()


# @app.before_first_request
def create_tables():
    print(db)
    db.create_all()
    import_data = ImportData(os.getcwd() + '/Model/data')
    # import_data.import_user_type()
    # import_data.import_authors()
    # import_data.import_categories()
    # import_data.import_books()
    # import_data.import_book_categories()
    import_data.fix_book_image()
    # import_data.import_user()
    # import_data.import_rating_books()


# ---------------------------AUTH----------------------------
auth_ns.add_resource(UserValidationResource.UserRegistration, '/registration')
auth_ns.add_resource(UserValidationResource.UserLogin, '/login')
auth_ns.add_resource(UserValidationResource.UserLogoutAccess, '/logout/access')
auth_ns.add_resource(UserValidationResource.UserLogoutRefresh, '/logout/refresh')
auth_ns.add_resource(UserValidationResource.TokenRefresh, '/token/refresh')

# ----------------------------ADMIN---------------------------
# admin_ns.add_resource(UserValidationResource.GetAllUsers, '/getallusers')
# admin_ns.add_resource(UserValidationResource.SecretResource, '/secret')
# admin_ns.add_resource(UserValidationResource.GetAllUsers, '/delallusers')

# ---------------------------BOOKS---------------------------
# books_ns.add_resource(BookResource.NewBook, '/new')
books_ns.add_resource(BookResource.AllBooksByCategory, '/category')
books_ns.add_resource(BookResource.TopBooks, '/top')
books_ns.add_resource(BookResource.DetailsBook, '/details')
books_ns.add_resource(BookResource.RatingsBook, '/ratings')
books_ns.add_resource(BookResource.RatingsStatBook, '/ratings/stat')
books_ns.add_resource(BookResource.DetailsCategoriesBook, '/details/categories')

# ---------------------------CATEGORIES---------------------------
categories_ns.add_resource(CategoryResource.AllCategory, '/')
categories_ns.add_resource(CategoryResource.PopularCategories, '/popular')

# ---------------------------AUTHORS---------------------------
authors_ns.add_resource(AuthorResource.TopAuthor, '/top')

# --------------------------SEARCH------------------------------------
# search_ns.add_resource(SearchResource.Search, '/')

# --------------------------WAREHOUSES---------------------------
warehouses_ns.add_resource(WarehousesResource.WarehousesBook, '/book')
warehouses_ns.add_resource(WarehousesResource.WarehousesEmail, '/email')
warehouses_ns.add_resource(WarehousesResource.WarehouseNew, '/new')

# ---------------------------USER---------------------------
user_ns.add_resource(UserResource.UserProfile, '/profile')
user_ns.add_resource(UserResource.UserRate, '/rate')
user_ns.add_resource(UserResource.UserLend, '/lend')
user_ns.add_resource(UserResource.UserBorrow, '/borrow')
user_ns.add_resource(UserResource.UserReturn, '/return')
user_ns.add_resource(UserResource.UserRatings, '/ratings')
user_ns.add_resource(UserResource.UserRatingsStat, '/ratings/stats')
user_ns.add_resource(UserResource.UserLendings, '/lendings')
user_ns.add_resource(UserResource.UserBorrowings, '/borrowings')
user_ns.add_resource(UserResource.UserUpdateProfile, '/profile/update')
user_ns.add_resource(UserResource.UserTransactions, '/transactions')
user_ns.add_resource(UserResource.UserRemoveWarehouse, '/remove')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
