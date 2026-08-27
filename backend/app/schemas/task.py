from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    note: str | None = None
    completed: bool = False


class TaskUpdateAll(BaseModel):
    title: str
    note: str | None = None
    completed: bool


class TaskUpdatePartial(BaseModel):
    title: str | None = None
    note: str | None = None
    completed: bool | None = None


class TaskRead(BaseModel):
    id: int
    title: str
    note: str | None = None
    completed: bool

    model_config = ConfigDict(from_attributes=True)


class BulkTaskCreate(BaseModel):
    tasks: list[TaskCreate]