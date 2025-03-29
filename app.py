from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2 import OperationalError
from models.db import db
from models.models import Book
from models.recommender import search_books
from models.data_loader import load_all_data
import os
import time


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:postgres@db:5432/books_db"
)
app.config["SQLALCHEMY_ECHO"] = True
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
#     "DATABASE_URL", "postgresql://postgres:postgres@localhost/books_db"
# )
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def wait_for_postgres():
    print("⏳ Waiting for PostgreSQL to be ready...")
    while True:
        try:
            conn = psycopg2.connect(
                dbname="books_db",
                user="postgres",
                password="postgres",
                host="db",  # <--- This is the issue
                port="5432",
            )
            conn.close()
            print("✅ PostgreSQL is ready!")
            break
        except OperationalError as e:
            print("PostgreSQL not ready, retrying in 1 second...")
            print(e)
            time.sleep(1)


def ensure_data_loaded():
    with app.app_context():
        book_count = Book.query.count()
        if book_count == 0:
            print("📂 No books found in the database. Loading data from CSVs...")
            load_all_data()
        else:
            print(f"✅ Found {book_count} books in the database.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query", "")
    results = search_books(query)
    return jsonify([{"title": book.title} for book in results])


@app.route("/reset-db", methods=["POST"])
def reset_db():
    load_all_data()
    return jsonify({"status": "success", "message": "Database reset complete!"})


if __name__ == "__main__":
    # try:
    print("🚀 Starting Flask app...")
    wait_for_postgres()
    with app.app_context():
        db.create_all()

    ensure_data_loaded()
    #     print("✅ Flask is now running on http://localhost:5050")
    app.run(host="0.0.0.0", port=5000)
    # except Exception as e:
    #     print("❌ App failed to start:", str(e))
