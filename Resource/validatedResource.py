from flask_restplus import Resource, reqparse
from Model.models import user_details
from Model.revokedTokenModel import revokedTokenModel
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
import requests
import json

parse = reqparse.RequestParser();
parse.add_argument('firstname', help="This field cannot be blank", required=True)
parse.add_argument('lastname', help="This field cannot be blank", required=True)
parse.add_argument('email', help="This field cannot be blank", required=True)
parse.add_argument('password', help="This field cannot be blank", required=True)


class UserRegistration(Resource):
    def post(self):
        data = parse.parse_args()
        if user_details.find_by_email(data['email']):
            return {'message': 'User already exists'}
        new_user = user_details(
            firstname=data['firstname'],
            lastname=data['lastname'],
            email=data['email'],
            password=user_details.generate_hash(data['password'], ),
            user_type_id=3,
            cash=0
        )
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': 'Success',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'message': 'Something went wrong'}, 500


loginParse = reqparse.RequestParser();
loginParse.add_argument('email', help="This field cannot be blank", required=True)
loginParse.add_argument('password', help="This field cannot be blank", required=True)


class UserLogin(Resource):
    def post(self):
        data = loginParse.parse_args()
        current_user = user_details.find_by_email(data['email'])
        if not current_user:
            return {'message': 'Not exist'}

        if user_details.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['email'])
            refresh_token = create_refresh_token(identity=data['email'])
            return {
                'message': 'Success',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = revokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = revokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return user_details.return_all()

    def delete(self):
        return user_details.delete_all()


class SecretResource(Resource):
    @jwt_required
    def get(self):
        try:
            current_user = get_jwt_identity()
            print(current_user)
        except:
            return {'message': 'Access token is revoked'}, 401
        return {
            'answer': 42
        }
