from pymongo import MongoClient
from dotenv import load_dotenv
import utils
import os
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

# Connect to MongoDB Atlas
client = MongoClient(os.getenv("MONGO_URI"))
db = client.edu_db
collection = db.materials

def upload_documents(file_path):
    """Upload a PDF to MongoDB Atlas with embeddings."""
    print(f"Uploading {file_path} to MongoDB Atlas...")
    
    documents = utils.semantic_chunking(file_path)
    
    # Clear previous data and insert new
    print("Clearing existing documents in the collection...")
    collection.delete_many({})
    collection.insert_many(documents)
    print(f"Uploaded {len(documents)} chunks to MongoDB.")

def query_documents(query, k=1):
    """Query MongoDB Atlas for relevant chunks."""
    print(f"Querying for: {query}")
    
    # Initialize vector store
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name="primary"
    )
    
    # Perform similarity search
    try:
        results = vector_store.similarity_search(query, k=k)
        print(f"Found {len(results)} results for query: {query}")
        
        if not results:
            print("No results found. Consider checking if embeddings were stored correctly and index exists.")
        
        for result in results:
            page_number = result.metadata.get('metadata', {}).get("page", "Unknown")
            print(f"Page: {page_number}")
            print(result.page_content)  # Print the retrieved chunk
            print("-" * 50)
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    pdf_path = "./OERs/ML_mod1.1.pdf"
    upload_documents(pdf_path)
    
    sample_query = "what maps the world into digital signals?"
    query_documents(sample_query)