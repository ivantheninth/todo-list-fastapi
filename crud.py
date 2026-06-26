from sqlalchemy import select
from database import SessionLocal
from models import Task
from schemas import TaskCreate, TaskUpdateAll, TaskUpdatePartial
from mapper import task_mapper

class TaskCrud:

    def create_task(self, task_data: TaskCreate):
        session = SessionLocal()

        try:
            task = task_mapper.to_model(task_data)



            session.add(task)
            session.commit()
            session.refresh(task)

            return task_mapper.to_read(task)

        finally:
            session.close()

    def update_whole_task(self, task_id: int, task_data: TaskUpdateAll):
        session = SessionLocal()

        try:
            task = session.get(Task, task_id)

            if task is None:
                return None

            task_mapper.update_model(task, task_data)

            session.commit()
            session.refresh(task)

            return task_mapper.to_read(task)

        finally:
            session.close()

    def update_task_partially(self, task_id: int, task_data: TaskUpdatePartial):
        session = SessionLocal()

        try:
            task = session.get(Task, task_id)

            if task is None:
                return None

            task_mapper.patch_model(task, task_data)

            session.commit()
            session.refresh(task)

            return task_mapper.to_read(task)

        finally:
            session.close()

    def get_all_tasks(self):
        session = SessionLocal()

        try:
            stmt = select(Task)
            result = session.execute(stmt)
            tasks = result.scalars().all()
            return [task_mapper.to_read(task) for task in tasks]
        finally:
            session.close()

    def get_task_by_id(self, task_id: int):
        session = SessionLocal()

        try:
            task = session.get(Task, task_id)

            if task is None:
                return None

            return task_mapper.to_read(task)

        finally:
            session.close()

    def mark_task_done(self, task_id: int):
        session = SessionLocal()

        try:
            task = session.get(Task, task_id)

            if task is None:
                return None

            task_mapper.mark_done(task)

            session.commit()
            session.refresh(task)

            return task_mapper.to_read(task)

        finally:
            session.close()


    def delete_task(self, task_id: int):
        session = SessionLocal()

        try:

            task = session.get(Task, task_id)

            if task is None:
                return None

            deleted_task = task_mapper.to_read(task)

            session.delete(task)
            session.commit()

            return deleted_task

        finally:
            session.close()

task_crud = TaskCrud()


