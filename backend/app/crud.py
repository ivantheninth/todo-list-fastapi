from sqlalchemy import select
from sqlalchemy.orm import Session

from app.mapper import task_mapper
from app.models import Task
from app.schemas import TaskCreate, TaskUpdateAll, TaskUpdatePartial


class TaskCrud:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def create_task(
        self,
        session: Session,
        task_data: TaskCreate,
    ):
        task = task_mapper.to_model(task_data)

        session.add(task)
        session.flush()

        return task_mapper.to_read(task)

    def update_whole_task(
        self,
        session: Session,
        task_id: int,
        task_data: TaskUpdateAll,
    ):
        task = session.get(Task, task_id)

        if task is None:
            return None

        task_mapper.update_model(task, task_data)
        session.flush()

        return task_mapper.to_read(task)

    def update_task_partially(
        self,
        session: Session,
        task_id: int,
        task_data: TaskUpdatePartial,
    ):
        task = session.get(Task, task_id)

        if task is None:
            return None

        task_mapper.patch_model(task, task_data)
        session.flush()

        return task_mapper.to_read(task)

    def get_all_tasks(
        self,
        session: Session,
    ):
        stmt = select(Task)
        result = session.execute(stmt)
        tasks = result.scalars().all()

        return [
            task_mapper.to_read(task)
            for task in tasks
        ]

    def get_task_by_id(
        self,
        session: Session,
        task_id: int,
    ):
        task = session.get(Task, task_id)

        if task is None:
            return None

        return task_mapper.to_read(task)

    def mark_task_done(
        self,
        session: Session,
        task_id: int,
    ):
        task = session.get(Task, task_id)

        if task is None:
            return None

        task_mapper.mark_done(task)
        session.flush()

        return task_mapper.to_read(task)

    def delete_task(
        self,
        session: Session,
        task_id: int,
    ):
        task = session.get(Task, task_id)

        if task is None:
            return None

        deleted_task = task_mapper.to_read(task)

        session.delete(task)
        session.flush()

        return deleted_task


task_crud = TaskCrud()