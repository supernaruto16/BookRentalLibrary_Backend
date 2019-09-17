from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def sql_db():
    return db

def init(app):
    db.init_app(app)
