from .models import Book
from sqlalchemy import create_engine
import pandas as pd
import pandas as pd
import re
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_distances
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


def search_books(query):
    # Replace this with real ML logic
    return Book.query.filter(Book.title.ilike(f"%{query}%")).all()


def normalize_author(name):
    if pd.isna(name):
        return ""
    name = name.lower().strip()
    name = re.sub(r"[^\w\s]", "", name)  # remove punctuation
    name = re.sub(r"\s+", " ", name)  # collapse multiple spaces
    return name


class Recomender:
    def __init__(self, url):
        self.DATABASE_URL = (
            url  # "postgresql://postgres:postgres@localhost:15432/books_db"
        )
        self.loaded = False
        self.cluster_author_eps = 0.12
        self.top_n = 5
        self.is_trained = False
        pass

    def start_train(self):
        self.is_training = True
        self.get_data()
        self.pre_process()
        self.cluster_authors()
        self.make_matrix()
        self.train()
        self.is_trained = True
        self.is_training = False

    def get_data(self):
        # Create SQLAlchemy engine
        engine = create_engine(self.DATABASE_URL)

        # Load all three tables into Pandas DataFrames
        self.books_df = pd.read_sql("SELECT * FROM books", engine)
        self.users_df = pd.read_sql("SELECT * FROM users", engine)
        self.ratings_df = pd.read_sql("SELECT * FROM ratings", engine)
        print(
            f"Data loaded books rows={self.books_df.shape[0]} users rows={self.users_df.shape[0]} ratings rows={self.ratings_df.shape[0]}"
        )
        self.loaded = True

    def pre_process(self):
        if self.loaded == False:
            self.get_data()

        self.books_df[self.books_df.isna().any(axis=1)]

        filtered_df = self.books_df[
            self.books_df["book_author"].apply(lambda x: str(x).isdigit())
        ]

        # Fixing the Book-Author column
        if filtered_df.shape[0] > 0:
            self.books_df.drop(filtered_df.index, inplace=True)

            cols = filtered_df.columns.to_list()
            filtered_dfi = filtered_df.iloc[:, 3:7]
            new_col = []

            for i in range(4, len(cols)):
                new_col.append(cols[i])

            filtered_dfi.columns = new_col
            filtered_dfii = filtered_df.iloc[:, 0:4].copy()
            filtered_dfiif = pd.concat([filtered_dfii, filtered_dfi], axis=1)
            filtered_dfiif.loc[:, "year_of_publication"] = filtered_dfiif["book_author"]
            filtered_dfiif.loc[:, "book_author"] = filtered_dfiif["title"]

            self.books_df = pd.concat([self.books_df, filtered_dfiif], axis=0)

            self.books_df["year_of_publication"] = self.books_df[
                "year_of_publication"
            ].astype(int)

        self.books_df = self.books_df.dropna(subset=["book_author", "publisher"])

        self.books_df["content"] = (
            self.books_df["title"].fillna("")
            + " "
            + self.books_df["publisher"].fillna("")
            + " "
            + self.books_df["book_author"].fillna("")
        )

        self.books_df["title_clean"] = self.books_df["title"].str.lower().str.strip()
        # books["Title-Clean"] = books["Book-Title"].str.lower().str.strip()

    def cluster_authors(self):
        tqdm.pandas()

        self.books_df["author_clean"] = self.books_df["book_author"].apply(
            normalize_author
        )

        # Get unique authors
        unique_authors = self.books_df["author_clean"].dropna().unique()
        author_df = pd.DataFrame({"author_clean": unique_authors})

        # Load SBERT model
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(
            author_df["author_clean"].tolist(), show_progress_bar=True
        )

        # Cluster similar names using cosine distance
        clustering = DBSCAN(eps=self.cluster_author_eps, min_samples=1, metric="cosine")
        labels = clustering.fit_predict(embeddings)

        # Add cluster labels
        author_df["canonical_author_id"] = labels

        self.books_df = self.books_df.merge(author_df, on="author_clean", how="left")

        # self.books_df["canonical_author_id"] = author_df["canonical_author_id"]

        print(
            f"Cluster 1 count = {author_df[author_df['canonical_author_id'] == 1].shape[0]}"
        )

    def make_matrix(self):
        ratings_0 = self.ratings_df.copy()
        # Filter to popular books and active users
        book_counts = ratings_0["isbn"].value_counts()
        popular_books = book_counts[book_counts > 10].index
        ratings_0 = ratings_0[ratings_0["isbn"].isin(popular_books)]

        user_counts = ratings_0["user_id"].value_counts()
        active_users = user_counts[user_counts > 5].index
        ratings_0 = ratings_0[ratings_0["user_id"].isin(active_users)]

        df_merged = pd.merge(ratings_0, self.books_df, on="isbn", how="inner")
        df_merged.drop_duplicates(subset=["user_id", "title"], inplace=True)

        book_matrix = df_merged.pivot_table(
            columns="user_id", index="isbn", values="book_rating"
        )

        book_matrix.fillna(0, inplace=True)
        self.book_matrix = book_matrix

    def predict(self, isbn):
        # Colaborative
        try:
            row = self.book_matrix.index.get_loc(isbn)
            book_n = self.book_matrix.iloc[row, :].values.reshape(1, -1)
            distance, suggestion = self.model.kneighbors(book_n, n_neighbors=6)
            sug = self.books_df.iloc[suggestion[0][1:]].copy()
        except:
            distance = None
            sug = None

        # Content wise
        book_idx = self.books_df.index[self.books_df["isbn"] == isbn].tolist()[0]
        target_vector = self.tfidf_matrix[book_idx]
        cosine_similarities = cosine_similarity(
            target_vector, self.tfidf_matrix
        ).flatten()
        similar_indices = cosine_similarities.argsort()[::-1][1 : self.top_n + 1]
        similar_books = self.books_df.iloc[similar_indices].copy()

        # Same author
        canon_id = self.books_df.loc[book_idx, "canonical_author_id"]
        same_author = self.books_df[
            self.books_df["canonical_author_id"] == canon_id
        ].copy()
        same_author = same_author.sort_values(by="year_of_publication", ascending=False)

        return {
            "distance": distance,
            "suggestion": sug,
            "content": similar_books,
            "same_author": same_author,
        }

    def train(self):
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(self.books_df["content"])
        self.tfidf_matrix = tfidf_matrix

        sparse_book = csr_matrix(self.book_matrix)
        model = NearestNeighbors(
            algorithm="brute", metric="cosine", n_neighbors=5, n_jobs=-1
        )

        model.fit(sparse_book)
        self.model = model
