from fastapi import APIRouter, FastAPI, HTTPException, Header
from common.auth import authenticate
from .evaluate_service import evaluation
from .evaluate_utils import EvaluateRequest, Evaluation

router = APIRouter(
    prefix="/tasks",
    tags=["activity"],
    responses={ 400: {"description": "Bad Request"},
                401: {"description": "Unauthorized"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}},
)

@router.post("/evaluate", response_model=Evaluation)
async def evaluate( request: EvaluateRequest, access_key: str = Header(...) ):
    """
    Evaluation for a given activity.
    """
    try: 
        authenticate(access_key)
        result = evaluation(request)

    except Exception as e:
        if hasattr(e, "status_code"):
            raise HTTPException(status_code=e.status_code, detail=str(e))
        else:
            raise RuntimeError(f"Unexpected error: {e}")

    return result

def include_router(app: FastAPI):
    app.include_router(router)
