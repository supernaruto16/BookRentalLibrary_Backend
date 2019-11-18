from cerberus import Validator
from Model.models import *


def validate_email(email):
    v = Validator()
    v.schema = {
        "type": "string",
        "regex": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"
    }
    if v.validate(email):
        return True,
    else:
        return False, 'Email contain invalid characters'


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
    if not UserDetails.find_by_email(email):
        return False, 'Email does not exist'
    return True,


def validate_book_id(book_id):
    if not BookDetails.find_by_isbn(book_id):
        return False, 'Book does not exist'
    return True,


def validate_warehouse_available(id):
    bookwarehouse_details = BookWarehouse.find_by_id(id)
    if not bookwarehouse_details:
        return False, 'Book does not exist'

    if not bookwarehouse_details.status:
        return False, 'Book does not available'
    return True,
