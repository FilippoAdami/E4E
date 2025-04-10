from fastapi import APIRouter, FastAPI, HTTPException, Header
from common.auth import authenticate
from .define_syllabus_service import syllabus
from .define_syllabus_utils import DefineSyllabusRequest, Syllabus

router = APIRouter(
    prefix="/tasks",
    tags=["plan"],
    responses={ 400: {"description": "Bad Request"},
                401: {"description": "Unauthorized"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}},
)

@router.post("/define_syllabus", response_model=Syllabus)
async def define_syllabus( request: DefineSyllabusRequest, access_key: str = Header(...) ):
    """
    """
    try: 
        authenticate(access_key)
        result = syllabus(request)

    except Exception as e:
        if hasattr(e, "status_code"):
            raise HTTPException(status_code=e.status_code, detail=str(e))
        else:
            raise RuntimeError(f"Unexpected error: {e}")

    return result

def include_router(app: FastAPI):
    app.include_router(router)
