import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../common')))
from mongodb_connection import get_mongo_collection
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_huggingface import HuggingFaceEmbeddings

# Get the collection from the 'resources' database
collection = get_mongo_collection("edu_db", "materials")

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
    sample_query = "what maps the world into digital signals?"
    query_documents(sample_query)