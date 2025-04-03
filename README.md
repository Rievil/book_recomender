# Recommender App

This is a Flask-based recommender app that combines:
- Nearest-neighbor similarity based on user ratings
- Content-based similarity between books
- Author-based grouping for recommendations

The application runs in a Docker container. For first-time use, you need to build the container. It uses a Flask server connected to a PostgreSQL database, which serves as the backbone for the ML-powered recommendation system.

The machine learning logic is encapsulated in a `Recommender` class. After starting the container, an instance of this class is stored in the Flask app’s config. The recommender is independent from the app itself and manages its own connection to the database. You can also connect to an external database by specifying the correct connection string.

## Getting Started

To build the container:
```
docker-compose build
```

To run the app:
```
docker-compose up
```

The app’s web interface is exposed on port `5050` by default.

## Application Limits

The app is designed to train the recommender on a dataset stored in the database. This allows the database to be continuously updated with new records, and training can be triggered manually, or in the future, automatically (e.g. after 100 new ratings or book entries).

Right now:
- Training is triggered via the API call: `/train-recommender`
- Predictions are returned via: `/predict/<isbn>`, which outputs a JSON list of recommended books similar to the given ISBN

Currently, the app only works with books that already exist in the database. If a book outside the database is typed into the search bar, no results will be returned.

This can be improved using a content-based fallback, enabling the system to return recommendations even when the ISBN is not found in the database.

## Canonical Author Clustering

The original Kaggle dataset contains messy and inconsistent values for `Book-Author`. For example, J.R.R. Tolkien appears under many variants like "J R R Tolkien", "John Ronald Reuel Tolkien", or "J.R.R.Tolkien".

To address this, I applied clustering on normalized author names using the `all-MiniLM-L6-v2` model from the SentenceTransformers library (SBERT). This generates canonical versions of author names, and books can now be filtered using a canonical author ID (`canonical_author_id`).

## Simplicity Over Complexity

This repository includes development notebooks:
- `01-Exploration.ipynb` was used to explore the dataset, test preprocessing, and build a prototype recommender
- `02-Database-and-API.ipynb` focuses on database interaction, storing records, and testing API routes (via Postman)

Once the results were satisfactory, the logic was integrated into the app. The HTML, CSS, and JavaScript parts were quickly built and refined using ChatGPT to accelerate the process.

The recommender stacks results from three different strategies and removes duplicates by ISBN and title. This makes the system modular and easy to extend or modify on the fly.

Because the recommender can be tested in the running app, it’s also ready for real-world deployments where high traffic or frequent updates require retraining or switching model architectures dynamically.

## Knowledge Graph

I’ve experimented with building knowledge graphs to visually represent relationships between books. This makes it easier to explore or navigate across book clusters. One use case I considered was for a friend who’s a writer, to help her analyze related works and genres visually.

The graphs were generated using the `pyvis` package. I initially planned to integrate them into the app to show book cards and their position in a network of similar titles.

## The Kaggle Dataset

The app uses the "Book Recommendation Dataset" from Kaggle, which supports many different approaches to building recommender models. Some of these models are already explored in existing GitHub repositories or Kaggle kernels.

This project provides a framework to test and evaluate those approaches and present the results through a user-friendly interface. The Flask server can be extended into a full web app or reduced to a minimal backend controlled entirely via API calls.
