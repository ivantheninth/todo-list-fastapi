from sqlalchemy import select
from database import SessionLocal
from models import Task
from schemas import TaskCreate, TaskRead, TaskUpdateAll, TaskUpdatePartial

class TaskCrud:

    def task_to_read(self, task: Task):
        return TaskRead(
            id=task.id,
            title=task.title,
            note=task.note,
            completed=task.completed
        )

    def create_task(self, task_data: TaskCreate):
        session = SessionLocal()

        try:
            task = Task(
                title=task_data.title,
                note=task_data.note,
                completed=task_data.completed
            )

            session.add(task)
            session.commit()
            session.refresh(task)

            return self.task_to_read(task)

        finally:
            session.close()

    def update_whole_task(self, task_id: int, task_data: TaskUpdateAll):
        session = SessionLocal()

        try:
            task = session.get(Task, task_id)

            if task is None:
                return None

            task.title = task_data.title
            task.note = task_data.note
            task.completed = task_data.completed

            session.commit()
            session.refresh(task)

            return self.task_to_read(task)

        finally:
            session.close()

    def update_task_partially(self, task_id: int, task_data: TaskUpdatePartial):
        session = SessionLocal()

        try:
            task = session.get(Task, task_id)

            if task is None:
                return None

            if task_data.title is not None:
                task.title = task_data.title
            if task_data.note is not None:
                task.note = task_data.note
            if task_data.completed is not None:
                task.completed = task_data.completed

            session.commit()
            session.refresh(task)

            return self.task_to_read(task)

        finally:
            session.close()

    def get_all_tasks(self):
        session = SessionLocal()

        try:
            stmt = select(Task)
            result = session.execute(stmt)
            tasks = result.scalars().all()
            return [self.task_to_read(task) for task in tasks]
        finally:
            session.close()

    def get_task_by_id(self, task_id: int):
        session = SessionLocal()

        try:
            task = session.get(Task, task_id)

            if task is None:
                return None

            return self.task_to_read(task)

        finally:
            session.close()

    def mark_task_done(self, task_id: int):
        session = SessionLocal()

        try:
            task = session.get(Task, task_id)

            if task is None:
                return None

            task.completed = True
            session.commit()
            session.refresh(task)

            return self.task_to_read(task)

        finally:
            session.close()


    def delete_task(self, task_id: int):
        session = SessionLocal()

        try:

            task = session.get(Task, task_id)

            if task is None:
                return None

            deleted_task = self.task_to_read(task)

            session.delete(task)
            session.commit()

            return deleted_task

        finally:
            session.close()

task_crud = TaskCrud()


