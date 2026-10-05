from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str ##for the check point
    message: str

    age: int
    height: float
    weight: float

    goal: str
    activity_level: str
    experience_level: str