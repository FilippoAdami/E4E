import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../common')))
from mongodb_connection import get_mongo_collection
import upload_utils

# Get the collection from the 'resources' database
collection = get_mongo_collection("edu_db", "materials")

def upload_documents(file_path):
    """Upload a PDF to MongoDB Atlas with embeddings."""
    print(f"Uploading {file_path} to MongoDB Atlas...")
    
    documents = upload_utils.semantic_chunking(file_path)
    
    # Clear previous data and insert new
    print("Clearing existing documents in the collection...")
    collection.delete_many({})
    collection.insert_many(documents)
    print(f"Uploaded {len(documents)} chunks to MongoDB.")

if __name__ == "__main__":
    pdf_path = "../../OERs/ML_mod1.1.pdf"
    upload_documents(pdf_path)
