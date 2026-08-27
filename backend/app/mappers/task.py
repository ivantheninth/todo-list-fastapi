from app.db.models.task import Task
from app.schemas.task import (
    TaskCreate,
    TaskRead,
    TaskUpdateAll,
    TaskUpdatePartial,
)

class TaskMapper:

    def to_model(self, task_data: TaskCreate) -> Task:
        return Task(**task_data.model_dump())

    def to_read(self, task: Task) -> TaskRead:
        return TaskRead.model_validate(task)

    def update_model(self, task: Task, task_data: TaskUpdateAll) -> None:

        for key, value in task_data.model_dump().items():
            setattr(task, key, value)

    def patch_model(self, task: Task, task_data: TaskUpdatePartial) -> None:

        for key, value in task_data.model_dump(exclude_unset=True).items():
            setattr(task, key, value)


task_mapper = TaskMapper()