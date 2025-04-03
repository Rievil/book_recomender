from flask import Flask, render_template, request, jsonify, current_app
import psycopg2
from psycopg2 import OperationalError
from models.db import db
from models.models import Book
from models.recommender import search_books
from models.data_loader import load_all_data
from models.graph_builder import create_graph_table
import os
import time
from sqlalchemy import text
from models.recommender import Recomender
import threading

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:postgres@db:5432/books_db"
)
rc = Recomender(app.config["SQLALCHEMY_DATABASE_URI"])
app.config["RECOMENDER"] = rc
app.config["IS_TRAINING"] = False

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


@app.route("/train-recommender", methods=["POST"])
def trigger_training():
    print("🚀 Triggering recommender training...")

    def async_train():
        with app.app_context():
            app.config["IS_TRAINING"] = True
            rc = app.config["RECOMENDER"]
            rc.is_trained = False
            rc.start_train()  # <-- your .train() method
            app.config["IS_TRAINING"] = False
            print("✅ Recommender training complete.")

    with app.app_context():
        if app.config["IS_TRAINING"] == True:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Recommender is already training.",
                    }
                ),
                400,
            )

        if app.config["RECOMENDER"].is_trained == True:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Recommender is already trained.",
                    }
                ),
                400,
            )

    thread = threading.Thread(target=async_train)
    thread.start()
    print("✅ Finished training")
    return (
        jsonify(
            {
                "status": "started",
                "message": "Recommender training started in background.",
            }
        ),
        202,
    )


def ensure_data_loaded():
    with app.app_context():
        book_count = Book.query.count()
        if book_count == 0:
            print("📂 No books found in the database. Loading data from CSVs...")
            load_all_data(app)
        else:
            print(f"✅ Found {book_count} books in the database.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "")

    # Example fuzzy search logic
    results = Book.query.filter(Book.title.ilike(f"%{query}%")).limit(10).all()

    return jsonify([{"title": book.title, "isbn": book.isbn} for book in results])


@app.route("/predict/<isbn>")
def predict(isbn):
    rc = current_app.config["RECOMENDER"]
    res = rc.predict(isbn)
    return jsonify(res)


@app.route("/graph-data")
def graph_data():
    result = db.session.execute(text("SELECT source, target, value FROM graph"))
    links = [{"source": row[0], "target": row[1], "value": row[2]} for row in result]
    return jsonify(links)


@app.route("/reset-db", methods=["POST"])
def reset_db():
    with app.app_context():
        load_all_data(app)
    return jsonify({"status": "success", "message": "Database reset complete!"})


if __name__ == "__main__":
    # try:
    print("🚀 Starting Flask app...")
    wait_for_postgres()
    with app.app_context():
        db.create_all()

    ensure_data_loaded()

    with app.app_context():
        create_graph_table()
    #     print("✅ Flask is now running on http://localhost:5050")
    app.run(host="0.0.0.0", port=5000)
