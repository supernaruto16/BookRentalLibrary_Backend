from flask import Flask, jsonify, request, render_template
from flask_restplus import Resource, Api, fields, reqparse
from flask_cors import CORS
from DB_Connection.db import init, sql_db
from flask_jwt_extended import JWTManager
from Model.RevokedTokenModel import RevokedTokenModel
import json
from Resource import UserValidationResource, BookResource, CategoryResource, AuthorResource, ActionResource
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

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + data["user"] + ':' + data["password"] + '@localhost/'+ data["database"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

init(app)
jwt = JWTManager(app)


# @app.route('/')
# def helloworld():
#     return "Hello"


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)


api = Api(app, version='1.0', title='BookRental API',
          description='BookRental API')
auth_ns = api.namespace('auth', description='Authentication API')
books_ns = api.namespace('books', description='Books API')
user_ns = api.namespace('user', description='Users API')
authors_ns = api.namespace('authors', description='Authors API')
categories_ns = api.namespace('categories', description='Categories API')
admin_ns = api.namespace('admin', description='Admin API')


db = sql_db()


# @app.before_first_request
# def create_tables():
#     print(db)
#     db.create_all()
#     import_data = ImportData(os.getcwd() + '/Model/data')
#     import_data.import_user_type()
#     import_data.import_authors()
#     import_data.import_categories()
#     import_data.import_books()
#     import_data.import_book_categories()


auth_ns.add_resource(UserValidationResource.UserRegistration, '/registration')
auth_ns.add_resource(UserValidationResource.UserLogin, '/login')
auth_ns.add_resource(UserValidationResource.UserLogoutAccess, '/logout/access')
auth_ns.add_resource(UserValidationResource.UserLogoutRefresh, '/logout/refresh')
auth_ns.add_resource(UserValidationResource.TokenRefresh, '/token/refresh')
admin_ns.add_resource(UserValidationResource.GetAllUsers, '/getallusers')
admin_ns.add_resource(UserValidationResource.SecretResource, '/secret')
admin_ns.add_resource(UserValidationResource.GetAllUsers, '/delallusers')
books_ns.add_resource(BookResource.NewBook, '/new')
books_ns.add_resource(BookResource.AllBooksByCategory, '/category')
books_ns.add_resource(BookResource.TopBooks, '/top')
books_ns.add_resource(BookResource.DetailsBook, '/details')
categories_ns.add_resource(CategoryResource.AllCategory, '/')
categories_ns.add_resource(CategoryResource.PopularCategories, '/popular')
authors_ns.add_resource(AuthorResource.TopAuthor, '/top')
user_ns.add_resource(ActionResource.UserRating, '/book/rate')
user_ns.add_resource(ActionResource.UserAdd, '/book/add')
user_ns.add_resource(ActionResource.UserBorrow, '/book/borrow')
user_ns.add_resource(ActionResource.UserBookList, '/books')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
