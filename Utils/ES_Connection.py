import requests


ES_URL = 'http://3.1.80.54:1910'


def update_ratings_book(book_id, average_rating):
    _params = {
        'id': book_id,
        'rating': average_rating
    }
    resp = requests.get(ES_URL + '/update', params=_params)
    if resp.status_code == 200:
        return True
    return False


def update_lenders_book(book_id, lenders_num):
    _params = {
        'id': book_id,
        'lenders': lenders_num
    }
    resp = requests.get(ES_URL + '/update', params=_params)
    if resp.status_code == 200:
        return True
    return False
