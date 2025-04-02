from google import genai
from dotenv import load_dotenv
from .plan_course_utils import PlanCourseRequest, PlanCourseResponse, CoursePlan, NodeS, plan_course_prompt
from ..translate.translate_service import translate
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")

client = genai.Client(api_key=API_KEY)

def course_plan(request: PlanCourseRequest):
    if request.model is None:
        request.model = "gemini-2.0-flash"
    try:
        response = client.models.generate_content(
            model=request.model,
            contents= plan_course_prompt(request),
            config={
                'response_mime_type': 'application/json',
                'response_schema': PlanCourseResponse,
            }
        )
        generated_lesson: PlanCourseResponse = response.parsed
        #print(generated_lesson)
        
        # Map the nodes to their string version to ensure proper JSON serialization
        nodes = [NodeS(type=node.type.value, topic=node.topic, details=node.details, duration=node.duration) for node in generated_lesson.nodes]
        
        # Combine the data to create a final lesson plan
        final_lesson = CoursePlan(
            title=request.title,
            macro_subject=request.macro_subject,
            education_level=request.education_level.value,
            learning_outcome=request.learning_outcome.value,
            prerequisites=generated_lesson.prerequisites,
            nodes=nodes,
            language=request.language,
            context=request.context
        )

        # Translate the lesson plan if the language is not English
        if request.language.lower() != "english":
            translation = translate(final_lesson.model_dump_json(indent=4), request.language).translation
            #print(translation)
            # map the translation back to a FinalLesson object
            translated_lesson_plan = CoursePlan.model_validate_json(translation)
            final_lesson = translated_lesson_plan
        
    except Exception as e:
        raise

    return final_lesson
