import pandas as pd
import os
from .models import Book, User, Rating
from .db import db
from sqlalchemy import select, func


def clean_age(age):
    try:
        age = int(age)
        if 5 < age < 100:
            return age
    except:
        return None


def load_all_data():
    with db.engine.begin() as conn:
        stmt = select(func.count()).select_from(Book)
        book_count = conn.execute(stmt).scalar()
        if book_count > 0:
            print(f"✅ Skipping load — {book_count} books already in database.")
            return

    print("📂 Loading CSV files...")

    # Confirm files exist
    print("🔍 Checking file paths...")
    for f in ["Books.csv", "Users.csv", "Ratings.csv"]:
        full_path = os.path.join("data", f)
        print(f" - {full_path}: ", os.path.exists(full_path))

    try:
        books_df = pd.read_csv("data/Books.csv", low_memory=False, nrows=5000)
        users_df = pd.read_csv("data/Users.csv", low_memory=False, nrows=10000)
        ratings_df = pd.read_csv("data/Ratings.csv", low_memory=False, nrows=50000)
    except Exception as e:
        print("❌ Failed to load CSVs:", e)
        return

    # Ensure all user IDs in ratings exist in users
    valid_user_ids = set(users_df["User-ID"])
    ratings_df = ratings_df[ratings_df["User-ID"].isin(valid_user_ids)]

    # Ensure all ISBNs in ratings exist in books
    valid_isbns = set(books_df["ISBN"])
    ratings_df = ratings_df[ratings_df["ISBN"].isin(valid_isbns)]

    print(
        f"📊 Books: {len(books_df)}, Users: {len(users_df)}, Ratings: {len(ratings_df)}"
    )

    # ratings_df = ratings_df[ratings_df["Book-Rating"] > 0]

    # book_counts = ratings_df["ISBN"].value_counts()
    # popular_books = book_counts[book_counts > 50].index
    # ratings_df = ratings_df[ratings_df["ISBN"].isin(popular_books)]

    # user_counts = ratings_df["User-ID"].value_counts()
    # active_users = user_counts[user_counts > 100].index
    # ratings_df = ratings_df[ratings_df["User-ID"].isin(active_users)]

    # books_df = books_df[books_df["ISBN"].isin(ratings_df["ISBN"].unique())]
    # users_df = users_df[users_df["User-ID"].isin(ratings_df["User-ID"].unique())]

    print(
        f"✅ Filtered: {len(books_df)} books, {len(users_df)} users, {len(ratings_df)} ratings"
    )

    # db.drop_all()
    # db.create_all()

    books = [
        Book(
            isbn=row["ISBN"],
            title=row["Book-Title"],
            author=row["Book-Author"],
            year=(
                int(row["Year-Of-Publication"])
                if str(row["Year-Of-Publication"]).isdigit()
                else None
            ),
            publisher=row["Publisher"],
            image_url_s=row["Image-URL-S"],
            image_url_m=row["Image-URL-M"],
            image_url_l=row["Image-URL-L"],
        )
        for _, row in books_df.iterrows()
    ]
    print(f"📘 Saving {len(books)} books...")
    db.session.bulk_save_objects(books)

    users = [
        User(
            id=int(row["User-ID"]),
            location=row["Location"],
            age=row["Age"] if not pd.isna(row["Age"]) else None,
        )
        for _, row in users_df.iterrows()
    ]
    print(f"👤 Saving {len(users)} users...")
    db.session.bulk_save_objects(users)

    ratings = [
        Rating(
            user_id=int(row["User-ID"]),
            isbn=row["ISBN"],
            book_rating=int(row["Book-Rating"]),
        )
        for _, row in ratings_df.iterrows()
    ]
    print(f"⭐ Saving {len(ratings)} ratings...")
    db.session.bulk_save_objects(ratings)

    db.session.commit()
    print("✅ Data reloaded successfully.")
