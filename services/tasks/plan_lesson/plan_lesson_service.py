from google import genai
from dotenv import load_dotenv
from .plan_lesson_utils import PlanLessonRequest, PlanLessonResponse, LessonPlan, LessonPlanS, NodeS, plan_lesson_prompt
from ..translate.translate_service import translate
from ...llm_integration.gemini import GeminiLLM
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")

client = genai.Client(api_key=API_KEY)

def lesson_plan(request: PlanLessonRequest):
    model = request.model
    if model is None:
        model = "GEMINI"
    if model.capitalize() == "GEMINI":
        llm = GeminiLLM()
    else:
        llm = GeminiLLM()
    try:
        response: PlanLessonResponse = llm.generate_json(prompt=plan_lesson_prompt(request), response_model=PlanLessonResponse)
        
        # Map the nodes to their string version to ensure proper JSON serialization
        nodes = [NodeS(type=node.type.value, topic=node.topic, details=node.details, learning_outcome=node.learning_outcome.value, duration=node.duration) for node in response.nodes]
        
        # Combine the data to create a final lesson plan
        final_lesson = LessonPlanS(
            title=request.title,
            macro_subject=request.macro_subject,
            education_level=request.education_level.value,
            learning_outcome=request.learning_outcome.value,
            prerequisites=response.prerequisites,
            nodes=nodes,
            language=request.language,
            context=request.context
        )

        rt = LessonPlan(
            title=request.title,
            macro_subject=request.macro_subject,
            education_level=request.education_level,
            learning_outcome=request.learning_outcome,
            prerequisites=response.prerequisites,
            nodes=response.nodes,
            context=request.context
        )
        # Translate the lesson plan if the language is not English
        if request.language.lower() != "english":
            translation = translate(final_lesson.model_dump_json(indent=4), request.language, model).translation
            #print(translation)
            # map the translation back to a FinalLesson object
            translated_lesson_plan = LessonPlanS.model_validate_json(translation)
            final_lesson = translated_lesson_plan
        
    except Exception as e:
        raise

    return final_lesson
