import pandas as pd
import os
from .models import Book, User, Rating
from .db import db
from sqlalchemy import select, func
from tqdm import tqdm


def clean_age(age):
    try:
        age = int(age)
        if 5 < age < 100:
            return age
    except:
        return None


def load_all_data(app):
    # with db.engine.begin() as conn:
    #     stmt = select(func.count()).select_from(Book)
    #     book_count = conn.execute(stmt).scalar()
    #     if book_count > 0:
    #         print(f"✅ Skipping load — {book_count} books already in database.")
    #         return

    print("📂 Loading CSV files...")

    # Confirm files exist
    print("🔍 Checking file paths...")
    for f in ["Books.csv", "Users.csv", "Ratings.csv"]:
        full_path = os.path.join("data", f)
        print(f" - {full_path}: ", os.path.exists(full_path))

    try:
        books_df = pd.read_csv("data/Books.csv", low_memory=False)
        users_df = pd.read_csv("data/Users.csv", low_memory=False)
        ratings_df = pd.read_csv("data/Ratings.csv", low_memory=False)
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

    # Loading full dataset in db, filtering will be in querry
    print(
        f"Filtered: {len(books_df)} books, {len(users_df)} users, {len(ratings_df)} ratings"
    )
    with app.app_context():
        print("Dropping and creating tables...")
        db.drop_all()
        db.create_all()

        # Insert books with progress bar
        print(f"📘 Saving {len(books_df)} books...")
        for _, row in tqdm(
            books_df.iterrows(), total=len(books_df), desc="📚 Inserting books"
        ):
            book = Book(
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
            db.session.add(book)

        # Insert users with progress bar
        print(f"👤 Saving {len(users_df)} users...")
        for _, row in tqdm(
            users_df.iterrows(), total=len(users_df), desc="Inserting users"
        ):
            user = User(
                id=int(row["User-ID"]),
                location=row["Location"],
                age=row["Age"] if not pd.isna(row["Age"]) else None,
            )
            db.session.add(user)

        # Insert ratings with progress bar
        print(f"⭐ Saving {len(ratings_df)} ratings...")
        for _, row in tqdm(
            ratings_df.iterrows(), total=len(ratings_df), desc="Inserting ratings"
        ):
            rating = Rating(
                user_id=int(row["User-ID"]),
                isbn=row["ISBN"],
                book_rating=int(row["Book-Rating"]),
            )
            db.session.add(rating)

        db.session.commit()

    print("Data reloaded successfully.")
