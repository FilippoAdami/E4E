from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from .vector_search_service import query_documents
from dotenv import load_dotenv
import os

router = APIRouter(
    prefix="/vector_search",
    tags=["vector_search"],
    responses={404: {"description": "Not found"}},
)

class QueryRequest(BaseModel):
    query: str
    uri: str = None
    db_name: str = None
    collection_name: str = None

class QueryResult(BaseModel):
    page: int  # Page number extracted from metadata
    content: str  # Extracted page content

class QueryResponse(BaseModel):
    results: List[QueryResult]  # List of results with metadata and content

@router.post("/query", response_model=QueryResponse)
async def query_vector_search(request: QueryRequest):
    """
    Query a collection about a specific topic.

    - **query**: The query to search for
    - **uri**: MongoDB connection URI
    - **db_name**: Database name
    - **collection_name**: Collection name
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query must be provided")
    
    # Fallback to environment variables if empty
    if not request.uri or not request.db_name or not request.collection_name or request.uri == "" or request.db_name == "" or request.collection_name == "":
        print("Using environment variables for MongoDB connection details...")
        load_dotenv()
        request.uri = os.getenv("MONGO_URI", "")
        request.db_name = "edu_db"
        request.collection_name = "materials"

    try:
        # Ensure query_documents is awaited if it's an async function
        results = query_documents(request.query, request.uri, request.db_name, request.collection_name)
        # Extract structured data: page number and content
        extracted_results = [
            QueryResult(
                page=int(doc.metadata.get("metadata", {}).get("page", -1)),  # Default to -1 if missing
                content=doc.page_content
            )
            for doc in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return QueryResponse(results=extracted_results)

def include_router(app: FastAPI):
    app.include_router(router)
