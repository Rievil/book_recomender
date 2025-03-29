from .db import db


class Book(db.Model):
    __tablename__ = "books"
    isbn = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    author = db.Column("book_author", db.String)
    year = db.Column("year_of_publication", db.Integer)
    publisher = db.Column(db.String)
    image_url_s = db.Column(db.String)
    image_url_m = db.Column(db.String)
    image_url_l = db.Column(db.String)
    ratings = db.relationship("Rating", back_populates="book")


class User(db.Model):
    __tablename__ = "users"
    id = db.Column("user_id", db.Integer, primary_key=True)
    location = db.Column(db.String)
    age = db.Column(db.Integer)

    ratings = db.relationship("Rating", back_populates="user")


class Rating(db.Model):
    __tablename__ = "ratings"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    isbn = db.Column(db.String, db.ForeignKey("books.isbn"))
    book_rating = db.Column(db.Integer)

    user = db.relationship("User", back_populates="ratings")
    book = db.relationship("Book", back_populates="ratings")
