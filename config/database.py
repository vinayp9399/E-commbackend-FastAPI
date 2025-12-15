from pymongo import MongoClient

MONGO_URI="mongodb+srv://vinayp9399:mechanic%4093@vinaycluster.03uocxi.mongodb.net/bigcart?retryWrites=true&w=majority&appName=VinayCluster"

client = MongoClient(MONGO_URI)
db = client.bigcart

collection_name = db["todo_collection"]
users = db["users"]
products = db["products"]
carts = db["carts"]
wishlists = db["wishlists"]


