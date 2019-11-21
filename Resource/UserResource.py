from flask_jwt_extended import (jwt_required, get_jwt_identity)
from flask_restplus import Namespace, Resource, reqparse
from Utils.InputValidation import *


api = Namespace('user')


rating_req = reqparse.RequestParser()
rating_req.add_argument('book_id', required=True)
rating_req.add_argument('rating_num', type=int, required=True)
rating_req.add_argument('rating_comment')


class UserRate(Resource):
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

        # v = validate_existed_email(current_user)
        # if not v[0]:
        #     return {'message': 'User does not exist'}, 400

        rating_details = RatingDetails(book_id=data['book_id'],
                                       user_id=current_user[1],
                                       rating_num=data['rating_num'],
                                       rating_comment=data['rating_comment'])
        rating_details.save_to_db()
        return {'message': 'success'}, 200


lend_req = reqparse.RequestParser()
lend_req.add_argument('book_id', required=True)
lend_req.add_argument('price', type=int, required=True)
lend_req.add_argument('address', default="")
lend_req.add_argument('time_upload')


class UserLend(Resource):
    @jwt_required
    @api.expect(lend_req)
    def post(self):
        data = lend_req.parse_args()
        current_user = get_jwt_identity()
        # user_details = UserDetails.find_by_email(current_user)
        # if not user_details:
        #     return {'message': 'Email does not exist'}, 401

        v = validate_book_id(data['book_id'])
        if not v[0]:
            return {'message': v[1]}, 400

        book_warehouse = BookWarehouse(book_id=data['book_id'],
                                       owner_id=current_user[1],
                                       price=data['price'],
                                       time_upload=data['time_upload'],
                                       address=data['address'],
                                       is_validate=1,
                                       validator=1,
                                       status=1)
        book_warehouse.save_to_db()
        return {'message': 'success'}, 200


borrow_req = reqparse.RequestParser()
borrow_req.add_argument('warehouse_id', type=int, required=True)
borrow_req.add_argument('day_borrow')
borrow_req.add_argument("day_expected_return")
borrow_req.add_argument("address", required=True)


class UserBorrow(Resource):
    @jwt_required
    @api.expect(borrow_req)
    def post(self):
        data = borrow_req.parse_args()
        current_user = get_jwt_identity()

        # user_details = UserDetails.find_by_email(current_user)
        # if not user_details:
        #     return {'message': 'Email does not exist'}, 401

        warehouse_details = BookWarehouse.find_by_id(data['warehouse_id'])
        if not warehouse_details:
            return {'message': 'Book does not exist'}, 400

        if not warehouse_details.status:
            return {'message': 'Book does not available'}, 400

        borrow_details = BorrowDetails(warehouse_id=data['warehouse_id'],
                                       borrower_id=current_user[1],
                                       day_borrow=data['day_borrow'],
                                       day_expected_return=data['day_expected_return'],
                                       address=data['address'])
        borrow_details.save_to_db()
        warehouse_details.status = 0
        warehouse_details.save_to_db()
        return {'message': 'success'}, 200


lendings_parse = reqparse.RequestParser()
lendings_parse.add_argument('limit', type=int, default=5)
lendings_parse.add_argument('page', type=int, default=1)


class UserLendings(Resource):
    @jwt_required
    @api.expect(lendings_parse)
    def get(self):
        data = lendings_parse.parse_args()
        current_user = get_jwt_identity()
        return BookWarehouse.find_by_owner(current_user[1], data['limit'], data['page']), 200


borrowings_parse = reqparse.RequestParser()
borrowings_parse.add_argument('limit', type=int, default=5)
borrowings_parse.add_argument('page', type=int, default=5)


class UserBorrowings(Resource):
    @jwt_required
    @api.expect(borrowings_parse)
    def get(self):
        data = borrowings_parse.parse_args()
        current_user = get_jwt_identity()
        return BorrowDetails.find_by_borrower(current_user[1], data['limit'], data['page'])


ratings_parse = reqparse.RequestParser()
ratings_parse.add_argument('limit', type=int, default=5)
ratings_parse.add_argument('page', type=int, default=1)


class UserRatings(Resource):
    @jwt_required
    @api.expect(ratings_parse)
    def get(self):
        data = borrowings_parse.parse_args()
        current_user = get_jwt_identity()
        return RatingDetails.find_by_user(current_user[1], data['limit'], data['page'])
