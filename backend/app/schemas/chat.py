from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
)


AITaskTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=200,
    ),
]

AITaskNote = Annotated[
    str,
    StringConstraints(
        max_length=2000,
    ),
]


class AITask(BaseModel):
    title: AITaskTitle
    note: AITaskNote | None = None


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )


class ChatResponse(BaseModel):
    answer: str = Field(
        min_length=1,
        max_length=5000,
    )

    tasks: list[AITask] = Field(
        default_factory=list,
        max_length=100,
    )