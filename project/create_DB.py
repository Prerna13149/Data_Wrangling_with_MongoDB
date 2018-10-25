def get_db():
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.chicago
    print "chicago db is created"
    return db
