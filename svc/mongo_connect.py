import pymongo

def connectMongo():
	host = "127.0.0.1:27017"
	db = "user_data"

	url = "mongodb://" + host + "/" + db
	client = pymongo.MongoClient(url)
	db = client[db]
	return db

