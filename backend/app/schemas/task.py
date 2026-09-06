from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)


TaskTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=200,
    ),
]


TaskNote = Annotated[
    str,
    StringConstraints(
        max_length=2000,
    ),
]


class TaskCreate(BaseModel):
    title: TaskTitle
    note: TaskNote | None = None
    completed: bool = False


class TaskUpdateAll(BaseModel):
    title: TaskTitle
    note: TaskNote | None = None
    completed: bool


class TaskUpdatePartial(BaseModel):
    title: TaskTitle | None = None
    note: TaskNote | None = None
    completed: bool | None = None

    @field_validator("completed")
    @classmethod
    def completed_cannot_be_null(
        cls,
        value: bool | None,
    ) -> bool | None:
        if value is None:
            raise ValueError(
                "completed cannot be null"
            )

        return value


class TaskRead(BaseModel):
    id: int
    title: str
    note: str | None = None
    completed: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class BulkTaskCreate(BaseModel):
    tasks: list[TaskCreate] = Field(
        min_length=1,
        max_length=100,
    )