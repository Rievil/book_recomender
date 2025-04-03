# Recomender app
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

## The aplication limits
The aplication is designed to train the recomender on the dataset stored in db. By this way, the db can be populated by new records, and the training can be triggered either by time trigger, event (after 100 new ratings or book records for example). Right now the training is controled via API call "/train-recommender". The predict API call "/predict/<isbn>" return a JSON of predicted books, which are similar to the inputed ISBN. Right now, the aplication works only with books within the DB. If a unknown book is written in the search bar it will not return similar books. 

This could be solved by using content-based search if the ISBN is not present in the DB. The current kaggle dataset has a lot of messy information in fields Book-Title, Book-Author. Book-Author has many version of the same author, for example JRRR Tolkien. This name is a nice example for it is complex, and is stored in db multiple times. In order to look for similar authors, the normal filter would not work properly, so I have used clustering of normalized Book-Author names using SBERT model "all-MiniLM-L6-v2" from SentenceTransformer package. By clustering names, I have made more clear version of canonical author names, so its realativly easy to filter by canonical_id. 

## Simplicity over complexity
The whole repository has part focused on testing and development marked with number 01 and 02. The notebook 01 was used to explore the dataset, to test pre-processing steps and make working example of recommender version in bare-bones. The notebook 02 is focused on testing databse connection, storage of the data, and interacting with the running app and for testing their API routes. For this I used Postman aplication. 

Once I was happy with the results, which gave at least sufficient results, I have worked the solution into the app itself. The parts like HTML webpage and css style and .js script were done using chat GPT to speed up the build process and also for faster modificaitons.

The solution is right now stacking result from three differnet aproaches, and then droping same ISBN and Book-Title records. The solution can be quite easily modular this way, and we can change the selected process on the fly. The recomender can be also tested on running app, so In case that DB has high trafic, and the records are changing often and we have to update model or model architecture on daily basis, this design allows it. 

## Knowledge graph
I was also experimenting with knowledge graphs, to visualize simalarities of books visualy, beacuse this can help to explore and transverse across book clusters. I was also thinking about preparing this for my friend writer, to help her assess the books by this way. The generated html were done using pyvis package. Originaly I wanted to implement those in the recomender as well, to show book cards and their position on map of books.

## The kaggle dataset 
The "Book Recommendation Dataset" has a number of streams how to develop a recomender model. Those solutions are alredy present in some github repositories or on kaggle itself. I have prepared a framework in which those model designs can be tested and evaluated a presented to a user. The flask server can be also reduced to only minimum profile, controlled only by API calls. 


