import pandas as pd
from .models import Book, User, Rating
from .db import db


def clean_age(age):
    try:
        age = int(age)
        if 5 < age < 100:
            return age
    except:
        return None


def load_all_data():
    print("📂 Loading CSV files...")

    books_df = pd.read_csv("data/Books.csv", low_memory=False)
    users_df = pd.read_csv("data/Users.csv", low_memory=False)
    ratings_df = pd.read_csv("data/Ratings.csv", low_memory=False)

    print("🧹 Cleaning and filtering data...")

    # Clean age
    users_df["Age"] = users_df["Age"].apply(clean_age)

    # Remove implicit feedback (rating = 0)
    ratings_df = ratings_df[ratings_df["Book-Rating"] > 0]

    # Keep only popular books and active users
    book_counts = ratings_df["ISBN"].value_counts()
    popular_books = book_counts[book_counts > 50].index
    ratings_df = ratings_df[ratings_df["ISBN"].isin(popular_books)]

    user_counts = ratings_df["User-ID"].value_counts()
    active_users = user_counts[user_counts > 100].index
    ratings_df = ratings_df[ratings_df["User-ID"].isin(active_users)]

    # Filter books and users to only what's needed
    books_df = books_df[books_df["ISBN"].isin(ratings_df["ISBN"].unique())]
    users_df = users_df[users_df["User-ID"].isin(ratings_df["User-ID"].unique())]

    print("🧨 Dropping & recreating tables...")
    db.drop_all()
    db.create_all()

    print(f"📚 Loading {len(books_df)} books...")
    books_df = books_df.fillna("")
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
    db.session.bulk_save_objects(books)

    print(f"👤 Loading {len(users_df)} users...")
    users_df = users_df.fillna("")
    users = [
        User(
            id=int(row["User-ID"]),
            location=row["Location"],
            age=row["Age"] if not pd.isna(row["Age"]) else None,
        )
        for _, row in users_df.iterrows()
    ]
    db.session.bulk_save_objects(users)

    print(f"⭐ Loading {len(ratings_df)} ratings...")
    ratings = [
        Rating(
            user_id=int(row["User-ID"]),
            isbn=row["ISBN"],
            book_rating=int(row["Book-Rating"]),
        )
        for _, row in ratings_df.iterrows()
    ]

    db.session.bulk_save_objects(ratings)
    db.session.commit()
    print("✅ Data reloaded successfully.")
