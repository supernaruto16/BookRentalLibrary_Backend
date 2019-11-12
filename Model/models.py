from DB_Connection.db import sql_db
import bcrypt
from sqlalchemy import desc, func


db = sql_db()


class UserDetails(db.Model):
    __tablename__ = 'user_details'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type_id = db.Column(db.Integer, db.ForeignKey('user_type_details.user_type_id'), nullable=False)
    cash = db.Column(db.Integer, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    borrow_details = db.relationship("BorrowDetails", backref="user_details")
    owner = db.relationship("BookWarehouse", backref="owner_details", foreign_keys='BookWarehouse.owner_id')
    validator = db.relationship("BookWarehouse", backref="validator_details", foreign_keys='BookWarehouse.validator')
    ratings_details = db.relationship("RatingDetails", backref="user_details")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_number_of_users(cls):
        return cls.query(UserDetails).count()

    @classmethod
    def add_user(cls, username, password, first_name='', last_name=''):
        user = UserDetails.find_by_username(username)
        if user:
            return False, 'User already exists'

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_id = UserDetails.get_number_of_users() + 1
        user_type_id = 0
        cash = 0

        new_user = UserDetails(username=username, email=username, password=hashed_pw, user_id=user_id,
                               user_type_id=user_type_id, cash=cash, first_name=first_name, last_name=last_name)
        UserDetails.save_to_db(new_user)

    @classmethod
    def check_login(cls, username, password):
        user = UserDetails.find_by_username(username)
        if not user:
            return False, 'User does not exist!'
        if bcrypt.checkpw(password.encode('utf-8'), user.password):
            return True, 'success'
        else:
            return False, 'Incorrect password!'

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'email': x.username,
                'password': x.password,
                'first_name': x.first_name,
                'last_name': x.last_name,
                'cash': 0
            }

        return {'users': list(map(lambda x: to_json(x), UserDetails.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            print(num_rows_deleted)
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}


class BorrowDetails(db.Model):
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


class WarningDetails(db.Model):
    __tablename__ = 'warning_details'

    warning_id = db.Column(db.Integer, primary_key=True)
    warning_text = db.Column(db.TEXT)
    borrow_details = db.relationship("BorrowDetails", backref="warning_details")


class CategoryDetails(db.Model):
    __tablename__ = 'category_details'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(120))

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def to_json(cls, x):
        return {
            'category_id': x.category_id,
            'category_name': x.category_name
        }

    @classmethod
    def return_all(cls):
        return {'data': list(map(lambda x: cls.to_json(x), CategoryDetails.query.all()))}

    @classmethod
    def popular_categories(cls, limit, page):
        return db.session.query(
            func.count(BookCategories.category_id).label('num_books'), CategoryDetails.category_id, CategoryDetails.category_name
        ).join(CategoryDetails).group_by(BookCategories.category_id).order_by(desc('num_books')).limit(limit).offset((page - 1) * limit)


class UserTypeDetails(db.Model):
    __tablename__ = 'user_type_details'

    user_type_id = db.Column(db.Integer, primary_key=True)
    user_type_name = db.Column(db.String(120))
    user_details = db.relationship("UserDetails", backref="user_type_details")


class BookWarehouse(db.Model):
    __tablename__ = 'book_warehouse'

    warehouse_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(32), db.ForeignKey('book_details.ISBN'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'))
    is_validate = db.Column(db.Integer)
    status = db.Column(db.Integer)
    validator = db.Column(db.Integer, db.ForeignKey('user_details.user_id'))
    price = db.Column(db.Integer)
    address = db.Column(db.String(200))
    time_upload = db.Column(db.DateTime)
    borrow_details = db.relationship("BorrowDetails", backref="book_warehouse")


class RatingDetails(db.Model):
    __tablename__ = 'rating_details'

    user_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'), primary_key=True)
    book_id = db.Column(db.String(32), db.ForeignKey('book_details.ISBN'), primary_key=True)
    rating_num = db.Column(db.Integer)
    rating_comment = db.Column(db.TEXT)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class BookDetails(db.Model):
    __tablename__ = 'book_details'

    ISBN = db.Column(db.String(32), primary_key=True)
    book_title = db.Column(db.String(200))
    publication_year = db.Column(db.Integer)
    book_description = db.Column(db.TEXT)
    author_id = db.Column(db.Integer, db.ForeignKey("author_details.author_id"))
    book_cover = db.Column(db.String(200))
    ratings_details = db.relationship("RatingDetails", backref="book_details")
    book_warehouse = db.relationship("BookWarehouse", backref="book_details")

    def save_to_db(self):
        if not self.find_by_isbn(isbn=self.ISBN):
            db.session.add(self)
            db.session.commit()
            return True
        return False

    @classmethod
    def find_by_title(cls, title):
        return cls.query.filter_by(book_title=title).first()

    @classmethod
    def find_by_isbn(cls, isbn):
        return cls.query.filter_by(ISBN=isbn).first()

    @classmethod
    def to_json(cls, x):
        return {
            'ISBN': x.ISBN,
            'book_title': x.book_title,
            'publication_year': x.publication_year,
            'book_description': x.book_description,
            'book_cover': x.book_cover
        }

    @classmethod
    def return_all(cls, limit, page):
        return {'data': list(map(lambda x: cls.to_json(x), BookDetails.query.limit(limit).offset((page-1) * limit)))}

    @classmethod
    def return_new(cls, limit, page):
        return BookDetails.query.join(AuthorDetails).order_by(desc(BookDetails.publication_year)).limit(limit).offset((page-1) * limit)

    @classmethod
    def return_by_category(cls, category_id, limit, page):
        return BookDetails.query.join(BookCategories).join(AuthorDetails).filter(BookCategories.category_id == category_id).limit(limit).offset((page - 1) * limit)

    @classmethod
    def return_top_books(cls, limit, page):
        return cls.return_all(limit, page)


class BookCategories(db.Model):
    __tablename__ = 'book_categories'

    book_id = db.Column(db.String(32), db.ForeignKey('book_details.ISBN'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category_details.category_id'), primary_key=True)

    def save_to_db(self):
        if not self.check_dup(self.book_id, self.category_id):
            db.session.add(self)
            db.session.commit()
            return True
        return False

    @classmethod
    def check_dup(cls, book_id, category_id):
        return cls.query.filter_by(book_id=book_id, category_id=category_id).first()


class AuthorDetails(db.Model):
    __tablename__ = 'author_details'

    author_id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(120))
    book_details = db.relationship("BookDetails", backref="author_details")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def to_json(cls, x):
        return {
            'author_id': x.author_id,
            'author_name': x.author_name,
        }

    @classmethod
    def return_all(cls, limit, page):
        return {'data': list(map(lambda x: cls.to_json(x), AuthorDetails.query.limit(limit).offset((page-1) * limit)))}

    @classmethod
    def return_top(cls, limit, page):
        return cls.return_all(limit, page)
