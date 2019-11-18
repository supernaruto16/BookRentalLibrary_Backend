from flask_restplus import Resource, reqparse
from Model.models import UserDetails
from Model.models import RatingDetails
from Model.models import BookDetails
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_optional,
                                jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from Utils.InputValidation import *
import html


def validate_book_id(book_id):
    return True if BookDetails.find_by_isbn(book_id) else False


rating_req = reqparse.RequestParser()
rating_req.add_argument('book_id', type=int, required=True)
rating_req.add_argument('rating_num', type=int, required=True)
rating_req.add_argument('rating_comment')


class UserRating(Resource):
    @jwt_required
    def post(self):
        data = rating_req.parse_args()
        current_user = get_jwt_identity()
        # if not current_user:
        #     return {'message': 'You need login to rate this book', 'status': 'error'}, 401

        v = validate_book_id(data['book_id'])
        if not v[0]:
            return {'message': 'Book does not exsit!'}, 400

        user_details = UserDetails.find_by_email(current_user)
        if not user_details:
            return {'message': 'User does not exist'}, 400

        rating_details = RatingDetails(user_id=user_details.user_id, book_id=data['book_id'],
                                       rating_num=data['rating_num'],
                                       rating_comment=html.escape(data['rating_comment']))
        rating_details.save_to_db()
        return {'message': 'success'}, 200


add_req = reqparse.RequestParser()
add_req.add_argument('book_id', type=int, required=True)
add_req.add_argument('price', type=int, required=True)
add_req.add_argument('address')
add_req.add_argument('time_upload')


class UserAdd(Resource):
    @jwt_required
    def post(self):
        data = add_req.parse_args()
        current_user = get_jwt_identity()
        user_details = UserDetails.find_by_email(current_user)
        if not user_details:
            return {'message': 'Email does not exist'}, 401

        v = validate_book_id(data['book_id'])
        if not v[0]:
            return {'message': v[1]}, 400

        warehouse_id = BookWarehouse.get_total_num() + 1
        warehouse_details = BookWarehouse(book_id=data['book_id'],
                                          owner_id=user_details.user_id,
                                          price=data['price'],
                                          time_upload=data['time_upload'],
                                          address=html.escape(data['address']),
                                          is_validated=1,
                                          validator=1,
                                          status=1)
        warehouse_details.save_to_db()


borrow_req = reqparse.RequestParser()
borrow_req.add_argument('warehouse_id', type=int, required=True)
borrow_req.add_argument('day_borrow')
borrow_req.add_argument("day_expected_return")
borrow_req.add_argument("address")


class UserBorrow(Resource):
    @jwt_required
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

        borrow_id = BorrowDetails.get_total_num() + 1
        borrow_details = BorrowDetails(borrow_id=borrow_id,
                                       warehouse_id=data['warehouse_id'],
                                       user_id=user_details.user_id,
                                       day_borrow=data['day_borrow'],
                                       day_expected_return=data['day_expected_return'],
                                       address=html.escape(['address']))
        borrow_details.save_to_db()
        warehouse_details.status = 0
        warehouse_details.save_to_db()
        return {'message': 'success'}, 200

