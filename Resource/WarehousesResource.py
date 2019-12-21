from flask import jsonify
from flask_restplus import Namespace, Resource, reqparse
from flask_jwt_extended import jwt_required
from Utils.InputValidation import *


api = Namespace('warehouses')


book_parse = reqparse.RequestParser()
book_parse.add_argument('book_id', required=True)
book_parse.add_argument('limit', type=int, default=5)
book_parse.add_argument('page', type=int, default=1)


class WarehousesBook(Resource):
    @api.expect(book_parse)
    def get(self):
        data = book_parse.parse_args()
        v = validate_book_id(data['book_id'])
        if not v[0]:
            return {'message': v[1]}, 400
        book_details = v[1]
        warehouses = book_details.book_warehouse
        res = []
        for warehouse in warehouses:
            owner_details = UserDetails.find_by_id(warehouse.owner_id)
            if warehouse.status == 0:
                continue
            res.append({
                'warehouse_id': warehouse.warehouse_id,
                'price': warehouse.price,
                'borrowed_times': warehouse.borrowed_times,
                'email': owner_details.email,
                'status': warehouse.status,
            })
        return {'data': res}, 200


email_req = reqparse.RequestParser()
email_req.add_argument('email', required=True)
email_req.add_argument('limit', type=int, default=5)
email_req.add_argument('page', type=int, default=1)


class WarehousesEmail(Resource):
    @api.expect(email_req)
    def get(self):
        data = email_req.parse_args()
        v = validate_existed_email(data['email'])
        if not v[0]:
            return {'message': v[1]}, 200
        user_details = v[1]
        warehouses = user_details.owner
        return {'data': [warehouse.as_dict() for warehouse in warehouses]}, 200


new_req = reqparse.RequestParser()
new_req.add_argument('limit', type=int, default=5)
new_req.add_argument('page', type=int, default=1)


class WarehouseNew(Resource):
    @api.expect(new_req)
    def get(self):
        data = new_req.parse_args()
        return BookWarehouse.get_new_books(data['limit'], data['page']), 200
