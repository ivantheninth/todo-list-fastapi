from sqlalchemy import select
from database import SessionLocal
from models import Task
from schemas import TaskCreate, TaskRead, TaskUpdateAll, TaskUpdatePartial

def task_to_read(task: Task):
    return TaskRead(
        id=task.id,
        title=task.title,
        note=task.note,
        completed=task.completed
    )

def create_task(task_data: TaskCreate):
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

        return task_to_read(task)

    finally:
        session.close()

def update_whole_task(task_id: int, task_data: TaskUpdateAll):
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

        return task_to_read(task)

    finally:
        session.close()

def update_task_partially(task_id: int, task_data: TaskUpdatePartial):
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

        return task_to_read(task)

    finally:
        session.close()

def get_all_tasks():
    session = SessionLocal()

    try:
        stmt = select(Task)
        result = session.execute(stmt)
        tasks = result.scalars().all()
        return [task_to_read(task) for task in tasks]
    finally:
        session.close()

def get_task_by_id(task_id: int):
    session = SessionLocal()

    try:
        task = session.get(Task, task_id)

        if task is None:
            return None

        return task_to_read(task)

    finally:
        session.close()

def mark_task_done(task_id: int):
    session = SessionLocal()

    try:
        task = session.get(Task, task_id)

        if task is None:
            return None

        task.completed = True
        session.commit()
        session.refresh(task)

        return task_to_read(task)

    finally:
        session.close()


def delete_task(task_id: int):
    session = SessionLocal()

    try:

        task = session.get(Task, task_id)

        if task is None:
            return None

        deleted_task = task_to_read(task)

        session.delete(task)
        session.commit()

        return deleted_task

    finally:
        session.close()


