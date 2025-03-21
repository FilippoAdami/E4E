from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from .upload_service import upload_documents
from dotenv import load_dotenv
import os

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
    responses={404: {"description": "Not found"}},
)

class UploadRequest(BaseModel):
    file: str
    uri: str = None
    db_name: str = None
    collection_name: str = None

class UploadResponse(BaseModel):
    results: str

@router.post("/upload", response_model=UploadResponse)
async def upload_file(request: UploadRequest):
    """
    Upload a file (by path) and perform semantic chunking.

    - **file**: The path of the file to upload
    - **uri**: MongoDB connection URI
    - **db_name**: Database name
    - **collection_name**: Collection name
    """
    if not request.file.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Fallback to environment variables if empty
    if not request.uri or not request.db_name or not request.collection_name or request.uri == "" or request.db_name == "" or request.collection_name == "":
        print("Using environment variables for MongoDB connection details...")
        load_dotenv()
        request.uri = os.getenv("MONGO_URI", "")
        request.db_name = "edu_db"
        request.collection_name = "materials"

    try:
        # Ensure upload_documents is async, or remove await
        result = upload_documents(request.file, request.uri, request.db_name, request.collection_name)
        if result == 0:
            result = "Upload successful."
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return UploadResponse(results=result)

def include_router(app: FastAPI):
    app.include_router(router)
