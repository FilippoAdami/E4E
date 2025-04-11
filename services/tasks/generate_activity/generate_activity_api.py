from fastapi import APIRouter, FastAPI, HTTPException, Header
from common.auth import authenticate
from .generate_activity_service import activity
from .generate_activity_utils import GenerateActivityRequest, Activity

router = APIRouter(
    prefix="/tasks",
    tags=["activity"],
    responses={ 400: {"description": "Bad Request"},
                401: {"description": "Unauthorized"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}},
)

@router.post("/generate_activity", response_model=Activity)
async def generate_activity( request: GenerateActivityRequest, access_key: str = Header(...) ):
    """
    Generate activity for a given topic.
    """
    try: 
        authenticate(access_key)
        result = activity(request)

    except Exception as e:
        if hasattr(e, "status_code"):
            raise HTTPException(status_code=e.status_code, detail=str(e))
        else:
            raise RuntimeError(f"Unexpected error: {e}")

    return result

def include_router(app: FastAPI):
    app.include_router(router)
