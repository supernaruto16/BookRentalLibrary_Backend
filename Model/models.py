from sqlalchemy import desc, func
from DB_Connection.db import sql_db
from passlib.hash import pbkdf2_sha256 as sha256
from Utils.SqlEscape import *

db = sql_db()


class UserDetails(db.Model):
    __tablename__ = 'user_details'

    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    user_type_id = db.Column(db.Integer, db.ForeignKey('user_type_details.user_type_id'), nullable=False)
    cash = db.Column(db.Integer, default=0)
    borrow_details = db.relationship("BorrowDetails", backref="user_details")
    owner = db.relationship("BookWarehouse", backref="owner_details", foreign_keys='BookWarehouse.owner_id')
    validator = db.relationship("BookWarehouse", backref="validator_details", foreign_keys='BookWarehouse.validator')
    ratings_details = db.relationship("RatingDetails", backref="user_details")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns if c.name != 'password'}

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(user_id=id).first()

    @classmethod
    def get_number_of_users(cls):
        return cls.query.count()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'id': x.user_id,
                'email': x.email,
                'password': x.password,
                'first_name': x.first_name,
                'last_name': x.last_name,
                'user_type_id': x.user_type_id,
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

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class BorrowDetails(db.Model):
    __tablename__ = 'borrow_details'

    borrow_id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('book_warehouse.warehouse_id'))
    borrower_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'))
    day_borrow = db.Column(db.DateTime)
    day_expected_return = db.Column(db.DateTime)
    day_actual_return = db.Column(db.DateTime)
    warning_id = db.Column(db.Integer, db.ForeignKey('warning_details.warning_id'))
    address = db.Column(db.String(500))
    phone = db.Column(db.String(32))
    price = db.Column(db.Integer)
    payment_type = db.Column(db.String(64))
    status = db.Column(db.Integer)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    @classmethod
    def find_by_borrower(cls, borrower_id, limit, page):
        return {'data': list(map(lambda x: BorrowDetails.as_dict(x),
                                 cls.query.filter_by(borrower_id=borrower_id)
                                 .paginate(page=page, per_page=limit, error_out=False).items))}

    @classmethod
    def find_borrowings_by_borrower(cls, borrower_id, limit, page):
        return {'data': list(map(lambda x: BorrowDetails.as_dict(x),
                                 cls.query.filter_by(borrower_id=borrower_id, status=0)
                                 .paginate(page=page, per_page=limit, error_out=False).items))}

    @classmethod
    def find_by_warehouse(cls, warehouse_id, limit, page):
        return {'data': list(map(lambda x: BorrowDetails.as_dict(x),
                                 cls.query.filter_by(warehouse_id=warehouse_id)
                                 .paginate(page=page, per_page=limit, error_out=False).items))}

    @classmethod
    def get_total_num(cls):
        return cls.query.count()

    @classmethod
    def find_by_id(cls, borrow_id):
        return cls.query.filter_by(borrow_id=borrow_id).first()


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
    def find_by_id(cls, id):
        return cls.query.filter_by(category_id=id).first()

    @classmethod
    def to_json(cls, x):
        return {
            'category_id': x.category_id,
            'category_name': x.category_name
        }

    @classmethod
    def return_all(cls, limit, page):
        data = None
        if limit == -1:
            data = CategoryDetails.query.all()
        else:
            data = CategoryDetails.query.paginate(page=page, per_page=limit, error_out=False).items
        return {'data': list(map(lambda x: cls.to_json(x), data))}

    @classmethod
    def popular_categories(cls, limit, page):
        return db.session.query(
            func.count(BookCategories.category_id).label('num_books'),
            CategoryDetails.category_id,
            CategoryDetails.category_name
        ).join(CategoryDetails) \
            .group_by(BookCategories.category_id) \
            .order_by(desc('num_books')) \
            .paginate(page=page, per_page=limit, error_out=False).items


class UserTypeDetails(db.Model):
    __tablename__ = 'user_type_details'

    user_type_id = db.Column(db.Integer, primary_key=True)
    user_type_name = db.Column(db.String(120))
    user_details = db.relationship("UserDetails", backref="user_type_details")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(user_type_id=id).first()


class BookWarehouse(db.Model):
    __tablename__ = 'book_warehouse'

    warehouse_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.String(32), db.ForeignKey('book_details.ISBN'))
    owner_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'))
    status = db.Column(db.Integer)
    is_validate = db.Column(db.Integer)
    validator = db.Column(db.Integer, db.ForeignKey('user_details.user_id'))
    price = db.Column(db.Integer)
    address = db.Column(db.String(200))
    time_upload = db.Column(db.DateTime)
    borrowed_times = db.Column(db.Integer)
    borrow_details = db.relationship("BorrowDetails", backref="book_warehouse")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def change_status(self, new_status):
        self.status = new_status
        self.save_to_db()

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    @classmethod
    def find_by_owner(cls, owner_id, limit, page):
        return {'data': list(map(lambda x: BookWarehouse.as_dict(x),
                                 cls.query.filter_by(owner_id=owner_id)
                                 .paginate(page=page, per_page=limit, error_out=False).items))}

    @classmethod
    def find_by_id(cls, warehouse_id):
        return cls.query.filter_by(warehouse_id=warehouse_id).first()

    @classmethod
    def get_by_book_id(cls, book_id):
        return cls.query.filter_by(book_id=book_id).all()

    @classmethod
    def get_total_num(cls):
        return cls.query.count()

    @classmethod
    def get_new_books(cls, limit, page):
        return {'data': list(map(lambda x: BookWarehouse.as_dict(x),
                                 cls.query.paginate(page=page, per_page=limit, error_out=False).items))}


class RatingDetails(db.Model):
    __tablename__ = 'rating_details'

    user_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'), primary_key=True)
    book_id = db.Column(db.String(32), db.ForeignKey('book_details.ISBN'), primary_key=True)
    rating_num = db.Column(db.Integer)
    rating_comment = db.Column(db.TEXT)

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    @classmethod
    def find_by_user(cls, user_id, limit, page):
        return {'data': list(map(lambda x: RatingDetails.as_dict(x),
                                 cls.query.filter_by(user_id=user_id)
                                 .limit(limit).offset((page - 1) * limit)))}

    @classmethod
    def find_by_book(cls, book_id, limit, page):
        return list(map(lambda x: RatingDetails.as_dict(x),
                        cls.query.filter_by(book_id=book_id)
                        .paginate(page=page, per_page=limit, error_out=False).items))

    @classmethod
    def find_existing(cls, user_id, book_id):
        return cls.query.filter_by(user_id=user_id, book_id=book_id).first()

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
    cnt_5star = db.Column(db.Integer, default=0)
    cnt_4star = db.Column(db.Integer, default=0)
    cnt_3star = db.Column(db.Integer, default=0)
    cnt_2star = db.Column(db.Integer, default=0)
    cnt_1star = db.Column(db.Integer, default=0)
    ratings_details = db.relationship("RatingDetails", backref="book_details")
    book_warehouse = db.relationship("BookWarehouse", backref="book_details")

    def save_to_db(self, force=False):
        if force or not self.find_by_isbn(isbn=self.ISBN):
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    @classmethod
    def find_by_title(cls, title):
        return cls.query.filter_by(book_title=title).first()

    @classmethod
    def find_by_isbn(cls, isbn):
        return cls.query.filter_by(ISBN=isbn).first()

    @classmethod
    def search_by_title(cls, title, limit, page):
        return cls.query.filter(BookDetails.book_title.like('%' + escape_sqlalchemy_like(title) + '%')) \
            .paginate(page=page, per_page=limit, error_out=False).items

    @classmethod
    def search_by_isbn(cls, isbn, limit, page):
        return cls.query.filter(BookDetails.ISBN.like('%' + escape_sqlalchemy_like(isbn) + '%')) \
            .paginate(page=page, per_page=limit, error_out=False).items

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
        return {'data': list(map(lambda x: cls.to_json(x),
                                 BookDetails.query.paginate(page=page, per_page=limit, error_out=False).items))}

    @classmethod
    def return_new(cls, limit, page):
        return BookDetails.query.join(AuthorDetails) \
            .order_by(desc(BookDetails.publication_year)) \
            .paginate(page=page, per_page=limit, error_out=False).items

    @classmethod
    def return_by_category(cls, category_id, limit, page):
        return BookDetails.query.join(BookCategories) \
            .join(AuthorDetails) \
            .filter(BookCategories.category_id == category_id) \
            .paginate(page=page, per_page=limit, error_out=False).items

    @classmethod
    def get_book_details(cls, book_id):
        # book_id = html.escape(book_id)
        book_details = BookDetails.query.filter_by(ISBN=book_id).join(AuthorDetails)
        if not book_details:
            return False, 'Book does not exist'
        return True, book_details

    @classmethod
    def return_top_books(cls, limit, page):
        return BookDetails.query.paginate(page=page, per_page=limit, error_out=False).items
        #     join(RatingDetails)\
        # .limit(limit).offset((page - 1) * limit)
        #     # .order_by(desc(RatingDetails.rating_num))\
        # # return cls.return_all(limit, page)

    def add_rating(self, rating_num):
        rating_num = int(rating_num)
        if not 1 <= rating_num <= 5:
            return False
        cnt_rating = 'cnt_{num}star'.format(num=rating_num)
        setattr(self, cnt_rating, getattr(self, cnt_rating) + 1)

    def swap_rating(self, old_rating, new_rating):
        new_rating = int(new_rating)
        if not 1 <= new_rating <= 5:
            return False
        cnt_old = 'cnt_{num}star'.format(num=old_rating)
        cnt_new = 'cnt_{num}star'.format(num=new_rating)
        setattr(self, cnt_old, getattr(self, cnt_old) - 1)
        setattr(self, cnt_new, getattr(self, cnt_new) + 1)
        return True


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
    def find_by_book_id(cls, book_id):
        return cls.query.filter_by(book_id=book_id).all()

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
    def find_by_id(cls, author_id):
        return cls.query.filter_by(author_id=author_id).first()

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    @classmethod
    def search_by_name(cls, name, limit, page):
        return cls.query.filter(AuthorDetails.author_name.like('%' + escape_sqlalchemy_like(name) + '%')) \
            .paginate(page=page, per_page=limit, error_out=False).items

    @classmethod
    def to_json(cls, x):
        return {
            'author_id': x.author_id,
            'author_name': x.author_name,
        }

    @classmethod
    def return_all(cls, limit, page):
        return {'data': list(map(lambda x: cls.to_json(x),
                                 AuthorDetails.query.paginate(page=page, per_page=limit, error_out=False).items))}

    @classmethod
    def return_top(cls, limit, page):
        return cls.return_all(limit, page)
