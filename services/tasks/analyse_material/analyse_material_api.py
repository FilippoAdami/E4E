from fastapi import APIRouter, FastAPI, HTTPException, Header
from common.auth import authenticate
from .analyse_material_service import analysis
from .analyse_material_utils import AnalyseMaterialRequest, AnalyseMaterialResponse

router = APIRouter(
    prefix="/tasks",
    tags=["material"],
    responses={ 400: {"description": "Bad Request"},
                401: {"description": "Unauthorized"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}},
)

@router.post("/analyse_material", response_model=AnalyseMaterialResponse)
async def analyse_material( request: AnalyseMaterialRequest, access_key: str = Header(...) ):
    """
    """
    try: 
        authenticate(access_key)

        if len(request.text) < 200:
            raise HTTPException(status_code=400, detail="Text must be at least 200 characters.")
        
        result = analysis(request)

    except Exception as e:
        if hasattr(e, "status_code"):
            raise HTTPException(status_code=e.status_code, detail=str(e))
        else:
            raise RuntimeError(f"Unexpected error: {e}")

    return result

def include_router(app: FastAPI):
    app.include_router(router)
