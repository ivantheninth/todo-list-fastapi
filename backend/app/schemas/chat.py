from pydantic import BaseModel, Field


class AITask(BaseModel):
    title: str
    note: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )


class ChatResponse(BaseModel):
    answer: str
    tasks: list[AITask] = Field(default_factory=list)