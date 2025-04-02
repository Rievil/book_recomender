from .models import GraphEdge, Book
from .db import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text


def create_graph_table():
    print("📡 Creating 'graph' table...")

    # Drop & recreate the table (optional, for dev)
    db.session.execute(text("DROP TABLE IF EXISTS graph"))
    # db.session.execute("DROP TABLE IF EXISTS graph")
    db.session.commit()
    db.create_all()

    # Example: author → book edges
    edges = []
    seen = set()

    books = Book.query.with_entities(Book.title, Book.author).all()

    for title, author in books:
        if title and author:
            edge_key = (author.strip(), title.strip())
            if edge_key not in seen:
                edges.append(
                    GraphEdge(source=author.strip(), target=title.strip(), value=1)
                )
                seen.add(edge_key)

    db.session.bulk_save_objects(edges)
    db.session.commit()
    print(f"✅ Inserted {len(edges)} relationships into 'graph'.")
