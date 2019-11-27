import sys

from flask_restplus import Namespace, Resource, reqparse
from Model.models import UserDetails
from Model.RevokedTokenModel import RevokedTokenModel
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from Utils.InputValidation import *
import requests
import json


api = Namespace('auth')

parse = reqparse.RequestParser()
parse.add_argument('firstname', help="This field cannot be blank", required=True)
parse.add_argument('lastname', help="This field cannot be blank", required=True)
parse.add_argument('email', help="This field cannot be blank", required=True)
parse.add_argument('password', help="This field cannot be blank", required=True)


class UserRegistration(Resource):
    @api.expect(parse)
    def post(self):
        data = parse.parse_args()
        v = validate_new_email(data['email'])
        if not v[0]:
            return {'message': v[1]}, 400
        new_user = UserDetails(
            first_name=data['firstname'],
            last_name=data['lastname'],
            email=data['email'],
            password=UserDetails.generate_hash(data['password'], ),
            user_type_id=1,
            cash=1000
        )
        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=(new_user.email, new_user.user_id))
            refresh_token = create_refresh_token(identity=(new_user.email, new_user.user_id))
            return {
                'message': 'Success',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            e = sys.exc_info()[0]
            print(f'Error : {e}')
            return {'message': 'Something went wrong'}, 500


loginParse = reqparse.RequestParser()
loginParse.add_argument('email', help="This field cannot be blank", required=True)
loginParse.add_argument('password', help="This field cannot be blank", required=True)


class UserLogin(Resource):
    @api.expect(loginParse)
    def post(self):
        data = loginParse.parse_args()
        current_user = UserDetails.find_by_email(data['email'])
        if not current_user:
            return {'message': 'Email does not exist'}, 401

        if UserDetails.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=(data['email'], current_user.user_id))
            refresh_token = create_refresh_token(identity=(data['email'], current_user.user_id))
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
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
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


class GetAllUsers(Resource):
    def get(self):
        return UserDetails.return_all()


class DelAllUsers(Resource):
    def delete(self):
        return UserDetails.delete_all()


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
