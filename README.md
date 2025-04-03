### Recomender app
This is a recommender Flask app, which combines a nearest neibrehood for rated books by users, content similarity of content of books and books from same author. The aplication is build in docker contianer, so for first iniciazition its needed to build the container. The app is based on Flask python server with connection to Postogre database. This works as a main backbone of ML aplication. The ML tool is made in form of class Recomender, which is after running the container stored in config of Flask. The Recommender is independent on the aplication, and has its own connection to the db. The db, can be placed also elsewhere, then the recomender need the proper connection string url. 

To build the container:
```
docker-compose build
```

To run the app:
```
docker-compose up
```

The app wepbage is mapped to 5050 port on local.

The aplication is designed to train the recomender on the dataset stored in db. By this way, the db can be populated by new records, and the training can be triggered either by time trigger, event (after 100 new ratings or book records for example). Right now the training is controled via API call "/train-recommender". 

