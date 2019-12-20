from cerberus import Validator
from flask_restplus import ValidationError

from Model.models import *
import re
import html

PATTERN = dict()
PATTERN['email'] = re.compile("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$")


def validate_email(email):
    if not PATTERN['email'].match(email):
        return False, 'Email contain invalid characters'
    return True,


def validate_new_email(email):
    v = validate_email(email)
    if not v[0]:
        return v
    if UserDetails.find_by_email(email):
        return False, 'Email already existed'
    return True,


def validate_existed_email(email):
    v = validate_email(email)
    if not v[0]:
        return v
    user_details = UserDetails.find_by_email(email)
    if not user_details:
        return False, 'Email does not exist'
    return True, user_details


def validate_book_id(book_id):
    # book_id = html.escape(book_id)
    book_details = BookDetails.find_by_isbn(book_id)
    if not book_details:
        return False, 'Book does not exist'
    return True, book_details


def validate_warehouse_available(id):
    bookwarehouse_details = BookWarehouse.find_by_id(id)
    if not bookwarehouse_details:
        return False, 'Book does not exist'

    if not bookwarehouse_details.status:
        return False, 'Book does not available'
    return True,


def validate_role(email, role):
    user_details = UserDetails.find_by_email(email)
    user_type_details = UserTypeDetails.find_by_id(user_details.user_type_id)
    if not user_type_details or user_type_details.type_name != role:
        return False, 'Need %s authorization' % role
    return True,


def validate_warehouse_id_list(value):
    item_schema = {
        'type': 'dict',
        'schema': {
            'warehouse_id': {'type': 'integer', 'required': True},
            'num_days_borrow': {'type': 'integer', 'min': 1, 'required': True}
        }
    }
    list_schema = {
        'data': {
            'type': 'list',
            "schema": item_schema,
            'required': True
        }
    }
    wrap_value = {'data': value}
    # print(wrap_value)
    v = Validator(list_schema)
    if v.validate(wrap_value):
        return value
    raise ValidationError("Missing or bad parameter in the warehouse_id list")
