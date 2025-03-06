from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB Client instance (shared for all databases)
client = MongoClient(os.getenv("MONGO_URI"))

def get_mongo_db(db_name):
    """Returns a specific MongoDB database."""
    return client[db_name]

def get_mongo_collection(db_name, collection_name):
    """Returns a collection from a specific database."""
    db = get_mongo_db(db_name)
    return db[collection_name]
