from DB_Connection.db import sql_db
from passlib.hash import pbkdf2_sha256 as sha256

db = sql_db()


class user_details(db.Model):
    __tablename__ = 'user_details'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    user_type_id = db.Column(db.Integer, db.ForeignKey('user_type_details.user_type_id'))
    cash = db.Column(db.Integer)
    borrow_details = db.relationship("borrow_details", backref="user_details")
    owner = db.relationship("book_warehouse", backref="owner")
    validator = db.relationship("book_warehouse", backref="validator")
    ratings_details = db.relationship("ratings_details", backref="user_details")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email = email).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'email': x.username,
                'password': x.password,
                'first_name': x.first_name,
                'last_name' : x.last_name,
                'cash' : 0
            }

        return {'users': list(map(lambda x: to_json(x), user_details.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            print(num_rows_deleted)
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

class borrow_details(db.Model):
    __tablename__ = 'borrow_details'

    borrow_id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('book_warehouse.warehouse_id'))
    borrower_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'))
    day_borrow = db.Column(db.DateTime)
    day_expected_return = db.Column(db.DateTime)
    day_actual_return = db.Column(db.DateTime)
    warning_id = db.Column(db.Integer)
    address = db.Column(db.String(500))
    status = db.Column(db.Integer, db.ForeignKey('warning_details.warning_id'))


class warning_details(db.Model):
    __tablename__ = 'warning_details'

    warning_id = db.Column(db.Integer, primary_key=True)
    warning_text = db.Column(db.TEXT)
    borrow_details = db.relationship("borrow_details", backref="warning_details")

class category_details(db.Model):
    __tablename__ = 'category_details'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(120))
    book_details = db.relationship("book_details", backref="category_details")

class user_type_details(db.Model):
    __tablename__ = 'user_type_details'

    user_type_id = db.Column(db.Integer, primary_key=True)
    user_type_name = db.Column(db.String(120))
    user_details = db.relationship("user_details", backref="user_type_details")


class book_warehouse(db.Model):
    __tablename__ = 'book_warehouse'

    warehouse_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book_details.ISBN'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'))
    is_validate = db.Column(db.Integer)
    status = db.Column(db.Integer)
    validator = db.Column(db.Integer, db.ForeignKey('user_details.user_id'))
    price = db.Column(db.Integer)
    address = db.Column(db.String(200))
    time_upload = db.Column(db.DateTime)
    borrow_details = db.relationship("borrow_details", backref="book_warehouse")


class ratings_details(db.Model):
    __tablename__ = 'ratings_details'

    user_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book_details.ISBN'), primary_key=True)
    rating_num = db.Column(db.Integer)
    rating_comment = db.Column(db.TEXT)

class book_details(db.Model):
    __tablename__ = 'book_details'

    ISBN = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(200))
    publication_year = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey("category_details.category_id"))
    book_description = db.Column(db.TEXT)
    author_id = db.Column(db.Integer, db.ForeignKey("author_details.author_id"))
    book_cover = db.Column(db.String(200))
    ratings_details = db.relationship("ratings_details", backref="book_details")
    book_warehouse = db.relationship("book_warehouse", backref="book_details")

class author_details(db.Model):
    __tablename__ = 'author_details'

    author_id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(120))
    book_details = db.relationship("book_details", backref="author_details")












