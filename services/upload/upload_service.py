from common.mongodb_connection import get_mongo_collection

from .upload_utils import semantic_chunking

def upload_documents(file_path, uri, db_name, collection_name):
    """Upload a PDF to MongoDB Atlas with embeddings."""
    print(f"Uploading {file_path} to MongoDB Atlas...")
    # Connect to MongoDB
    collection = get_mongo_collection(db_name, collection_name, uri)
    print("Connected to MongoDB.")
    documents = semantic_chunking(file_path)
    
    # Clear previous data and insert new
    print("Clearing existing documents in the collection...") 
    collection.delete_many({})
    collection.insert_many(documents)
    print(f"Uploaded {len(documents)} chunks to MongoDB.")
    return 0
