from .models import Book


def search_books(query):
    # Replace this with real ML logic
    return Book.query.filter(Book.title.ilike(f"%{query}%")).all()
