from pydantic import BaseModel
from ..common_enums import EducationLevel, LearningOutcome, TypeOfActivity
from pydantic import BaseModel
from typing import List

class Node(BaseModel):
    type: TypeOfActivity
    topic: str
    details: str
    learning_outcome: LearningOutcome
    duration: int

class NodeS(BaseModel):
    type: str
    topic: str
    details: str
    learning_outcome: str
    duration: int

class PlanLessonResponse(BaseModel):
    nodes: List[Node]
    prerequisites: List[str]

    def to_json(self):
        return self.model_dump()

class Topic(BaseModel):
    topic: str
    explanation: str

    def __str__(self):
        return f"{self.topic} - {self.explanation}."

    def to_json(self):
        return self.model_dump()

class PlanLessonRequest(BaseModel):
    topics: List[Topic]
    learning_outcome: LearningOutcome
    language: str = "English"
    macro_subject: str
    title: str
    education_level: EducationLevel
    context: str
    model: str = None

    def to_json(self):
        return self.model_dump()

class LessonPlanS(BaseModel):
    title: str
    macro_subject: str
    education_level: str
    learning_outcome: str
    prerequisites: List[str]
    nodes: List[NodeS]    
    language: str = "English"
    context: str

class LessonPlan(BaseModel):
    title: str
    macro_subject: str
    education_level: EducationLevel
    learning_outcome: LearningOutcome
    prerequisites: List[str]
    nodes: List[Node]
    context: str

def plan_lesson_prompt(request: PlanLessonRequest):
   prompt = f"""You are an expert educator and instructional designer specialized in {request.macro_subject}. 
Your expertise lies in creating **structured, engaging, and pedagogically sound lesson plans**. 

### Task
Generate a **comprehensive lesson plan** for the topic: **'{request.title}'**, ensuring it aligns with best teaching practices for a **{request.education_level}** audience.  
The **main goal** is to help the audience achieve: **'{request.learning_outcome}'**, knowing your audience is: **'{request.context}'**.

### Lesson Plan Structure
Since you are highly organized, you will structure the lesson as a **logical sequence of nodes**, ensuring an effective balance between instruction and engagement.  
Each **node** consists of:  
- **TypeOfActivity**: choose an appropriate **TypeOfActivity** from the list below, balancing between content delivery and more interactive activities.  
- **Topic**: Select from the provided list.
- **Details**: Suggest a tailored explanation approach for this audience.  
- **Learning Outcome**: The desired learning outcome for this specific node. Note that not all the nodes will be about an equally important topic, so balance the learning outcomes accordingly.
- **Duration**: The minimum time (in minutes) needed for this node.

### Provided Resources
Here are the **topics** to be covered:
{"\n".join(str(topic) for topic in request.topics)}

Here are the available **TypeOfActivity** options:
{", ".join(e.value for e in TypeOfActivity)}

Here are the available **Learning Outcome** options:
{", ".join(e.value for e in LearningOutcome)}

### Prerequisites  
Now that you know how the lesson will be, list the key **prerequisites** your audience should already be familiar with (keep it concise).  
"""
   return prompt

"""Test text:
{
  "topics": [
    {
      "topic": "Who Were the Romans?",
      "explanation": "The Romans were people who lived in the city of Rome and built a huge empire across Europe, Africa, and Asia.",
      "learning_outcome": "the ability to recall or recognize simple facts and definitions"
    },
    {
      "topic": "The Roman Army",
      "explanation": "Roman soldiers, called legionaries, wore armor, carried shields, and marched in strong formations.",
      "learning_outcome": "the ability to recall or recognize simple facts and definitions"
    },
    {
      "topic": "Roman Roads",
      "explanation": "The Romans built straight and strong roads so that soldiers and traders could travel easily across the empire.",
      "learning_outcome": "the ability to recall or recognize simple facts and definitions"
    },
    {
      "topic": "Gladiators and the Colosseum",
      "explanation": "Gladiators were fighters who entertained people in big arenas like the Colosseum by battling each other or wild animals.",
      "learning_outcome": "the ability to recall or recognize simple facts and definitions"
    },
    {
      "topic": "Roman Gods and Myths",
      "explanation": "The Romans believed in many gods like Jupiter, Mars, and Venus and told exciting myths about them.",
      "learning_outcome": "the ability to recall or recognize simple facts and definitions"
    },
    {
      "topic": "Daily Life in Ancient Rome",
      "explanation": "Roman people lived in houses, went to the market, and enjoyed food like bread, cheese, and olives.",
      "learning_outcome": "the ability to recall or recognize simple facts and definitions"
    },
    {
      "topic": "The Fall of the Roman Empire",
      "explanation": "The Roman Empire became too big to control and eventually fell because of attacks, weak leaders, and other problems.",
      "learning_outcome": "the ability to recall or recognize simple facts and definitions"
    }
  ],
  "learning_outcome": "the ability to recall or recognize simple facts and definitions",
  "language": "English",
  "macro_subject": "History",
  "title": "The Roman Empire",
  "education_level": "elementary school",
  "context": "very easily distracted, but responds well to playful and interactive lessons",
  "model": "gemini-2.0-flash"
}
"""

