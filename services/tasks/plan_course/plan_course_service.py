from google import genai
from dotenv import load_dotenv
from .plan_course_utils import PlanCourseRequest, PlanCourseResponse, CoursePlan, CoursePlanS, plan_course_prompt
from ..translate.translate_service import translate
from ...llm_integration.gemini import GeminiLLM
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")

client = genai.Client(api_key=API_KEY)

def course_plan(request: PlanCourseRequest):
    model = request.model
    if model is None:
        model = "GEMINI"
    if model.capitalize() == "GEMINI":
        llm = GeminiLLM()
    else:
        llm = GeminiLLM()
    try:
        response: PlanCourseResponse = llm.generate_json(prompt=plan_course_prompt(request), response_model=PlanCourseResponse)
        #print("Response",response)
        #print("-"*50)
        # map nodes to their string version to ensure proper JSON serialization
        nodess = [node.model_dump() for node in response.nodes]

        # Combine the data to create a final lesson plan
        final_course = CoursePlanS(
            title=request.title,
            macro_subject=request.macro_subject,
            education_level=request.education_level.value,
            learning_outcome=request.learning_outcome.value,
            number_of_lessons=request.number_of_lessons,
            duration_of_lesson=request.duration_of_lesson,
            prerequisites=response.prerequisites,
            nodes=nodess,
            language=request.language
        )

        rt = CoursePlan(
            title=request.title,
            macro_subject=request.macro_subject,
            education_level=request.education_level,
            learning_outcome=request.learning_outcome,
            number_of_lessons=request.number_of_lessons,
            duration_of_lesson=request.duration_of_lesson,
            prerequisites=response.prerequisites,
            nodes=response.nodes
        )

        # Translate the lesson plan if the language is not English
        if request.language.lower() != "english":
            translation = translate(final_course.model_dump_json(indent=4), request.language).translation
            #print(translation)
            # map the translation back to a FinalLesson object
            
            print("-"*50)
            print(translation)
            print("-"*50)
            translated_course_plan = CoursePlanS.model_validate_json(translation)
            final_course = translated_course_plan
            
    except Exception as e:
        raise

    return final_course
