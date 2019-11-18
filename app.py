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


@app.route('/')
def helloworld():
    return "Hello"


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)


api = Api(app, version='1.0', title='BookRental API',
          description='BookRental API'
          )
ns = api.namespace('api', description='BookRental API')

db = sql_db()


# @app.before_first_request
# def create_tables():
#     print(db)
#     db.create_all()
#     import_data = ImportData(os.getcwd() + '/Model/data')
#     import_data.import_authors()
#     import_data.import_categories()
#     import_data.import_books()
#     import_data.import_book_categories()


ns.add_resource(UserValidationResource.UserRegistration, '/registration')
ns.add_resource(UserValidationResource.UserLogin, '/login')
ns.add_resource(UserValidationResource.UserLogoutAccess, '/logout/access')
ns.add_resource(UserValidationResource.UserLogoutRefresh, '/logout/refresh')
ns.add_resource(UserValidationResource.TokenRefresh, '/token/refresh')
ns.add_resource(UserValidationResource.AllUsers, '/users')
ns.add_resource(UserValidationResource.SecretResource, '/secret')
ns.add_resource(BookResource.NewBook, '/books/new')
ns.add_resource(CategoryResource.AllCategory, '/categories')
ns.add_resource(CategoryResource.PopularCategories, '/categories/popular')
ns.add_resource(BookResource.AllBooksByCategory, '/books/category')
ns.add_resource(BookResource.TopBooks, '/books/top')
ns.add_resource(AuthorResource.TopAuthor, '/authors/top')
ns.add_resource(ActionResource.UserRating, '/book/rating')
ns.add_resource(ActionResource.UserAdd, '/book/add')
ns.add_resource(ActionResource.UserBorrow, '/book/borrow')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
