from flask_restplus import Namespace, Resource, reqparse
from Model.models import UserDetails
from Model.models import RatingDetails
from Model.models import BookDetails
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_optional,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from Utils.InputValidation import *
import html


api = Namespace('user')

list_parse = reqparse.RequestParser()
list_parse.add_argument('limit', type=int, default=5)
list_parse.add_argument('page', type=int, default=1)


class UserBookList(Resource):
    @jwt_required
    @api.expect(list_parse)
    def get(self):
        data = list_parse.parse_args()
        current_user = get_jwt_identity()
        user_details = UserDetails.find_by_email(current_user)
        if not user_details:
            return {'message': 'Email does not exist'}, 401
        return BookWarehouse.find_by_owner(user_details.user_id, data['limit'], data['page']), 200


rating_req = reqparse.RequestParser()
rating_req.add_argument('book_id', required=True)
rating_req.add_argument('rating_num', type=int, required=True)
rating_req.add_argument('rating_comment')


class UserRating(Resource):
    @jwt_required
    @api.expect(rating_req)
    def post(self):
        data = rating_req.parse_args()
        current_user = get_jwt_identity()
        # if not current_user:
        #     return {'message': 'You need login to rate this book', 'status': 'error'}, 401

        v = validate_book_id(data['book_id'])
        if not v[0]:
            return {'message': 'Book does not exsit!'}, 400

        v = validate_existed_email(current_user)
        if not v[0]:
            return {'message': 'User does not exist'}, 400

        rating_details = RatingDetails(book_id=data['book_id'],
                                       rating_num=data['rating_num'],
                                       rating_comment=html.escape(data['rating_comment']))
        rating_details.save_to_db()
        return {'message': 'success'}, 200


add_req = reqparse.RequestParser()
add_req.add_argument('book_id', required=True)
add_req.add_argument('price', type=int, required=True)
add_req.add_argument('address', default="")
add_req.add_argument('time_upload')


class UserAdd(Resource):
    @jwt_required
    @api.expect(add_req)
    def post(self):
        data = add_req.parse_args()
        current_user = get_jwt_identity()
        user_details = UserDetails.find_by_email(current_user)
        if not user_details:
            return {'message': 'Email does not exist'}, 401

        v = validate_book_id(data['book_id'])
        if not v[0]:
            return {'message': v[1]}, 400

        book_warehouse = BookWarehouse(book_id=data['book_id'],
                                       owner_id=user_details.user_id,
                                       price=data['price'],
                                       time_upload=data['time_upload'],
                                       address=html.escape(data['address']),
                                       is_validate=1,
                                       validator=1,
                                       status=1)
        book_warehouse.save_to_db()
        return {'message': 'success'}, 200


borrow_req = reqparse.RequestParser()
borrow_req.add_argument('warehouse_id', type=int, required=True)
borrow_req.add_argument('day_borrow')
borrow_req.add_argument("day_expected_return")
borrow_req.add_argument("address", default="")


class UserBorrow(Resource):
    @jwt_required
    @api.expect(borrow_req)
    def post(self):
        data = borrow_req.parse_args()
        current_user = get_jwt_identity()

        user_details = UserDetails.find_by_email(current_user)
        if not user_details:
            return {'message': 'Email does not exist'}, 401

        warehouse_details = BookWarehouse.find_by_id(id)
        if not warehouse_details:
            return {'message': 'Book does not exist'}, 400

        if not warehouse_details.status:
            return {'message': 'Book does not available'}, 400

        borrow_details = BorrowDetails(warehouse_id=data['warehouse_id'],
                                       user_id=user_details.user_id,
                                       day_borrow=data['day_borrow'],
                                       day_expected_return=data['day_expected_return'],
                                       address=html.escape(data['address']))
        borrow_details.save_to_db()
        warehouse_details.status = 0
        warehouse_details.save_to_db()
        return {'message': 'success'}, 200
