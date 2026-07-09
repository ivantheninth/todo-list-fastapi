from sqlalchemy import select
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Task
from schemas import TaskCreate, TaskUpdateAll, TaskUpdatePartial
from mapper import task_mapper


class TaskCrud:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def _save_new_task(self, session: Session, task: Task) -> None:
        session.add(task)
        session.commit()
        session.refresh(task)

    def _commit_task_changes(self, session: Session, task: Task) -> None:
        session.commit()
        session.refresh(task)

    def _delete_task(self, session: Session, task: Task) -> None:
        session.delete(task)
        session.commit()

    def create_task(self, task_data: TaskCreate):
        with SessionLocal() as session:

            task = task_mapper.to_model(task_data)
            self._save_new_task(session, task)
            return task_mapper.to_read(task)

    def update_whole_task(self, task_id: int, task_data: TaskUpdateAll):
        with SessionLocal() as session:
            task = session.get(Task, task_id)

            if task is None:
                return None

            task_mapper.update_model(task, task_data)
            self._commit_task_changes(session, task)

            return task_mapper.to_read(task)

    def update_task_partially(self, task_id: int, task_data: TaskUpdatePartial):
        with SessionLocal() as session:

            task = session.get(Task, task_id)

            if task is None:
                return None

            task_mapper.patch_model(task, task_data)

            self._commit_task_changes(session, task)

            return task_mapper.to_read(task)

    def get_all_tasks(self):
        with SessionLocal() as session:

            stmt = select(Task)
            result = session.execute(stmt)
            tasks = result.scalars().all()

            return [task_mapper.to_read(task) for task in tasks]

    def get_task_by_id(self, task_id: int):
        with SessionLocal() as session:

            task = session.get(Task, task_id)

            if task is None:
                return None

            return task_mapper.to_read(task)

    def mark_task_done(self, task_id: int):
        with SessionLocal() as session:

            task = session.get(Task, task_id)

            if task is None:
                return None

            task_mapper.mark_done(task)
            self._commit_task_changes(session, task)

            return task_mapper.to_read(task)

    def delete_task(self, task_id: int):
        with SessionLocal() as session:

            task = session.get(Task, task_id)

            if task is None:
                return None

            deleted_task = task_mapper.to_read(task)
            self._delete_task(session, task)

            return deleted_task

task_crud = TaskCrud()


