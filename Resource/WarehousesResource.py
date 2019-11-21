from flask import jsonify
from flask_restplus import Namespace, Resource, reqparse
from flask_jwt_extended import jwt_required
from Utils.InputValidation import *


api = Namespace('warehouses')


book_req = reqparse.RequestParser()
book_req.add_argument('book_id', required=True)
book_req.add_argument('limit', type=int, default=5)
book_req.add_argument('page', type=int, default=1)


class WarehousesBook(Resource):
    @jwt_required
    @api.expect(book_req)
    def get(self):
        data = book_req.parse_args()
        v = validate_book_id(data['book_id'])
        if not v[0]:
            return {'message': v[1]}, 400
        book_details = v[1]
        warehouses = book_details.book_warehouses
        return jsonify([warehouse.as_dict() for warehouse in warehouses]), 200


email_req = reqparse.RequestParser()
email_req.add_argument('email', required=True)
email_req.add_argument('limit', type=int, default=5)
email_req.add_argument('page', type=int, default=1)


class WarehousesEmail(Resource):
    @jwt_required
    @api.expect(email_req)
    def get(self):
        data = email_req.parse_args()
        v = validate_existed_email(data['email'])
        if not v[0]:
            return {'message': v[1]}, 200
        user_details = v[1]
        warehouses = user_details.owner
        return jsonify([warehouse.as_dict() for warehouse in warehouses]), 200
