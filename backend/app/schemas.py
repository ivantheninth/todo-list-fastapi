# Validation of:
# created tasks
# Update all
#partial update
# read tasks

from pydantic import BaseModel, ConfigDict # BaseModel is used to describe the structure of data and automatically validate it.

#Used for creating a new task.

class TaskCreate(BaseModel):
    title: str
    note: str | None = None # this field could be empty, that's why we use None = None
    completed: bool = False

#  Update all task fields

class TaskUpdateAll(BaseModel):
    title: str
    note: str | None = None # this field could be empty, that's why we use None = None
    completed: bool

#update one task

class TaskUpdatePartial(BaseModel):
    title: str | None = None
    note: str | None = None
    completed: bool | None = None

# validation of read tasks

class TaskRead(BaseModel):
    id: int
    title: str
    note: str | None = None # this field could be empty, that's why we use None = None
    completed: bool
    model_config = ConfigDict(from_attributes=True)

