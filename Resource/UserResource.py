from flask_jwt_extended import (jwt_required, get_jwt_identity)
from flask_restplus import Namespace, Resource, reqparse
from Model.models import *
from Utils import AuthorizationDoc
from Utils.InputValidation import *
import datetime


api = Namespace('user')


profile_parse = reqparse.RequestParser()
profile_parse.add_argument('Authorization', type=str, location='headers', help='Bearer Access Token', required=True)


class UserProfile(Resource):
    @jwt_required
    @api.expect(profile_parse)
    @api.doc(security='Bearer Auth', authorizations=AuthorizationDoc.authorizations)
    def get(self):
        current_user = get_jwt_identity()
        user_details = UserDetails.find_by_id(current_user[1])
        return {'data': user_details.as_dict()}, 200


rating_req = reqparse.RequestParser()
rating_req.add_argument('Authorization', type=str, location='headers', help='Bearer Access Token', required=True)
rating_req.add_argument('book_id', required=True)
rating_req.add_argument('rating_num', type=int, required=True)
rating_req.add_argument('rating_comment')


class UserRate(Resource):
    @jwt_required
    @api.expect(rating_req)
    @api.doc(security='Bearer Auth', authorizations=AuthorizationDoc.authorizations)
    def post(self):
        data = rating_req.parse_args()
        current_user = get_jwt_identity()
        # if not current_user:
        #     return {'message': 'You need login to rate this book', 'status': 'error'}, 401

        v = validate_book_id(data['book_id'])
        if not v[0]:
            return {'message': 'Book does not exsit!'}, 400

        if data['rating_num'] < 0 or data['rating_num'] > 5:
            return {'message': 'Rating num must be between 0 or 5'}, 400

        rating_details = RatingDetails(book_id=data['book_id'],
                                       user_id=current_user[1],
                                       rating_num=data['rating_num'],
                                       rating_comment=data['rating_comment'])
        rating_details.save_to_db()
        return {'message': 'success'}, 200


lend_parse = reqparse.RequestParser()
lend_parse.add_argument('Authorization', type=str, location='headers', help='Bearer Access Token', required=True)
lend_parse.add_argument('book_id', required=True)
lend_parse.add_argument('price', type=int, required=True)
lend_parse.add_argument('address', default="")


class UserLend(Resource):
    @jwt_required
    @api.expect(lend_parse)
    @api.doc(security='Bearer Auth', authorizations=AuthorizationDoc.authorizations)
    def post(self):
        data = lend_parse.parse_args()
        current_user = get_jwt_identity()
        # user_details = UserDetails.find_by_email(current_user)
        # if not user_details:
        #     return {'message': 'Email does not exist'}, 401

        v = validate_book_id(data['book_id'])
        if not v[0]:
            return {'message': v[1]}, 400

        if data['price'] < 0:
            return {'message': 'price must be non-negative integer'}, 400

        day_upload = datetime.date.today()
        book_warehouse = BookWarehouse(book_id=data['book_id'],
                                       owner_id=current_user[1],
                                       price=data['price'],
                                       time_upload=day_upload,
                                       address=data['address'],
                                       is_validate=1,
                                       validator=1,
                                       status=1)
        book_warehouse.save_to_db()
        return {'message': 'success'}, 200


borrow_req = reqparse.RequestParser()
borrow_req.add_argument('Authorization', type=str, location='headers', help='Bearer Access Token', required=True)
borrow_req.add_argument('warehouse_id', type=int, required=True)
borrow_req.add_argument('num_days_borrow', type=int, required=True, default=5)
borrow_req.add_argument("address", required=True)


class UserBorrow(Resource):
    @jwt_required
    @api.expect(borrow_req)
    @api.doc(security='Bearer Auth', authorizations=AuthorizationDoc.authorizations)
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

        if warehouse_details.owner_id == current_user[1]:
            return {'message': 'Can not borrow your own book'}, 400

        user_details = UserDetails.find_by_id(current_user[1])
        if user_details.cash < warehouse_details.price:
            return {'message': 'Not enough cash'}, 400

        day_borrow = datetime.date.today()
        day_expected_return = day_borrow + datetime.timedelta(days=data['num_days_borrow'])
        borrow_details = BorrowDetails(warehouse_id=data['warehouse_id'],
                                       borrower_id=current_user[1],
                                       day_borrow=day_borrow,
                                       day_expected_return=day_expected_return,
                                       address=data['address'],
                                       status=0)
        warehouse_details.status = 0
        user_details.cash -= warehouse_details.price
        owner_details = UserDetails.find_by_id(warehouse_details.owner_id)
        owner_details.cash += warehouse_details.price

        user_details.save_to_db()
        owner_details.save_to_db()
        borrow_details.save_to_db()
        warehouse_details.save_to_db()
        return {'message': 'success'}, 200


return_req = reqparse.RequestParser()
return_req.add_argument('Authorization', type=str, location='headers', help='Bearer Access Token', required=True)
return_req.add_argument('borrow_id', type=int, required=True)
return_req.add_argument('address', required=True)


class UserReturn(Resource):
    @jwt_required
    @api.expect(return_req)
    @api.doc(security='Bearer Auth', authorizations=AuthorizationDoc.authorizations)
    def post(self):
        data = return_req.parse_args()
        current_user = get_jwt_identity()
        borrow_details = BorrowDetails.find_by_id(data['borrow_id'])
        if not borrow_details:
            return {'message': 'Invalid borrow id'}, 400
        elif borrow_details.borrower_id != current_user[1] or borrow_details.status != 0:
            return {'message': 'Invalid borrow id'}, 400
        warehouse_details = BookWarehouse.find_by_id(borrow_details.warehouse_id)
        if not warehouse_details:
            return {'message': 'Invalid borrow id'}, 400

        warehouse_details.status = 1
        borrow_details.status = 1
        borrow_details.day_actual_return = datetime.date.today()

        warehouse_details.save_to_db()
        borrow_details.save_to_db()
        return {'message': 'success'}, 200


lendings_parse = reqparse.RequestParser()
lendings_parse.add_argument('Authorization', type=str, location='headers', help='Bearer Access Token', required=True)
lendings_parse.add_argument('limit', type=int, default=5)
lendings_parse.add_argument('page', type=int, default=1)


class UserLendings(Resource):
    @jwt_required
    @api.expect(lendings_parse)
    @api.doc(security='Bearer Auth', authorizations=AuthorizationDoc.authorizations)
    def get(self):
        data = lendings_parse.parse_args()
        current_user = get_jwt_identity()
        return BookWarehouse.find_by_owner(current_user[1], data['limit'], data['page']), 200


borrowings_parse = reqparse.RequestParser()
borrowings_parse.add_argument('Authorization', type=str, location='headers', help='Bearer Access Token', required=True)
borrowings_parse.add_argument('limit', type=int, default=5)
borrowings_parse.add_argument('page', type=int, default=1)


class UserBorrowings(Resource):
    @jwt_required
    @api.expect(borrowings_parse)
    @api.doc(security='Bearer Auth', authorizations=AuthorizationDoc.authorizations)
    def get(self):
        data = borrowings_parse.parse_args()
        current_user = get_jwt_identity()
        return BorrowDetails.find_borrowings_by_borrower(current_user[1], data['limit'], data['page'])


ratings_parse = reqparse.RequestParser()
ratings_parse.add_argument('Authorization', type=str, location='headers', help='Bearer Access Token', required=True)
ratings_parse.add_argument('limit', type=int, default=5)
ratings_parse.add_argument('page', type=int, default=1)


class UserRatings(Resource):
    @jwt_required
    @api.expect(ratings_parse)
    @api.doc(security='Bearer Auth', authorizations=AuthorizationDoc.authorizations)
    def get(self):
        data = borrowings_parse.parse_args()
        current_user = get_jwt_identity()
        return RatingDetails.find_by_user(current_user[1], data['limit'], data['page'])


transactions_parse = reqparse.RequestParser()
transactions_parse.add_argument('Authorization', type=str, location='headers', help='Bearer Access Token', required=True)
transactions_parse.add_argument('mode', type=str, choices=('income', 'outcome'), required=True)
transactions_parse.add_argument('limit', type=int, default=5)
transactions_parse.add_argument('page', type=int, default=1)


class UserTransactions(Resource):
    @jwt_required
    @api.expect(transactions_parse)
    @api.doc(security='Bearer Auth', authorizations=AuthorizationDoc.authorizations)
    def get(self):
        data = transactions_parse.parse_args()
        current_user = get_jwt_identity()

        if data['mode'] == 'outcome':
            return BorrowDetails.find_by_borrower(current_user[1], data['limit'], data['page']), 200
        elif data['mode'] == 'income':
            warehouses = BookWarehouse.find_by_owner(current_user[1], None, None)
            incomes = dict()
            incomes['data'] = list()
            for warehouse in warehouses:
                sub_group = BorrowDetails.find_by_warehouse(warehouse.warehouse_id, None, None)
                incomes['data'] = incomes['data'] + sub_group['data']
            return incomes, 200
