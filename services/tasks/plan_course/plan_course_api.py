from fastapi import APIRouter, FastAPI, HTTPException, Header
from common.auth import authenticate
from .plan_course_service import course_plan
from .plan_course_utils import PlanCourseRequest, CoursePlan

router = APIRouter(
    prefix="/tasks",
    tags=["plan"],
    responses={ 400: {"description": "Bad Request"},
                401: {"description": "Unauthorized"},
                404: {"description": "Not found"},
                500: {"description": "Internal Server Error"}},
)

@router.post("/plan_course", response_model=CoursePlan)
async def plan_course( request: PlanCourseRequest, access_key: str = Header(...) ):
    """
    Plan a course based on the given request.
    topics: a list of topics to be covered in the lesson. Each topic should be a dictionary with the following keys:
        topic: the topic to be covered
        explanation: a brief explanation of the topic
        learning_outcome: the desired learning outcome
    learning_outcome: the desired learning outcome
    language: str = "English"
    macro_subject: the subject of the lesson
    title: the title of the lesson
    education_level: the education level of the audience
    context: the audience context
    """
    try: 
        authenticate(access_key)
        result = course_plan(request)

    except Exception as e:
        if hasattr(e, "status_code"):
            raise HTTPException(status_code=e.status_code, detail=str(e))
        else:
            raise RuntimeError(f"Unexpected error: {e}")

    return result

def include_router(app: FastAPI):
    app.include_router(router)
