from models import Task
from schemas import (
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

        task.title = task_data.title
        task.note = task_data.note
        task.completed = task_data.completed

    def patch_model(self, task: Task, task_data: TaskUpdatePartial) -> None:

        if task_data.title is not None:
            task.title = task_data.title

        if task_data.note is not None:
            task.note = task_data.note

        if task_data.completed is not None:
            task.completed = task_data.completed

    def mark_done(self, task: Task) -> None:
        task.completed = True

task_mapper = TaskMapper()