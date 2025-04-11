from fastapi import APIRouter, FastAPI, HTTPException, Header
from common.auth import authenticate
from .translate_service import translate
from .translate_utils import TranslateRequest, TranslateResponse

router = APIRouter(
    prefix="/tasks",
    tags=["material"],
    responses={ 400: {"description": "Bad Request"},
                401: {"description": "Unauthorized"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}},
)

@router.post("/translate", response_model=TranslateResponse)
async def translate_text( request: TranslateRequest, access_key: str = Header(...) ):
    """
    Translate a text into a specified language using the specified model.
    - **text**: The text to translate.
    - **model**: The model to use for translation. (optional)
    - **language**: The language you want to translate into. (optional, default: English)
    """
    try: 
        authenticate(access_key)
        result = translate(request.text, request.language, request.model)

    except Exception as e:
        if hasattr(e, "status_code"):
            raise HTTPException(status_code=e.status_code, detail=str(e))
        else:
            raise RuntimeError(f"Unexpected error: {e}")

    return result

def include_router(app: FastAPI):
    app.include_router(router)
