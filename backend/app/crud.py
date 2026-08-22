from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.mapper import task_mapper
from app.models import Task
from app.schemas import TaskCreate, TaskUpdateAll, TaskUpdatePartial


class TaskCrud:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    async def create_task(
        self,
        session: AsyncSession,
        task_data: TaskCreate,
    ):
        task = task_mapper.to_model(task_data)

        session.add(task)
        await session.flush()

        return task_mapper.to_read(task)

    async def create_tasks_bulk(
            self,
            session: AsyncSession,
            tasks_data: list[TaskCreate],
    ):
        created_tasks = []

        for task_data in tasks_data:
            task = await self.create_task(
                session,
                task_data,
            )

            created_tasks.append(task)

        return created_tasks

    async def update_whole_task(
        self,
        session: AsyncSession,
        task_id: int,
        task_data: TaskUpdateAll,
    ):
        task = await session.get(Task, task_id)

        if task is None:
            return None

        task_mapper.update_model(task, task_data)
        await session.flush()

        return task_mapper.to_read(task)

    async def update_task_partially(
        self,
        session: AsyncSession,
        task_id: int,
        task_data: TaskUpdatePartial,
    ):
        task = await session.get(Task, task_id)

        if task is None:
            return None

        task_mapper.patch_model(task, task_data)
        await session.flush()

        return task_mapper.to_read(task)

    async def get_all_tasks(
        self,
        session: AsyncSession,
    ):
        stmt = select(Task)
        result = await session.execute(stmt)
        tasks = result.scalars().all()

        return [
            task_mapper.to_read(task)
            for task in tasks
        ]

    async def get_task_by_id(
        self,
        session: AsyncSession,
        task_id: int,
    ):
        task = await session.get(Task, task_id)

        if task is None:
            return None

        return task_mapper.to_read(task)

    async def mark_task_done(
        self,
        session: AsyncSession,
        task_id: int,
    ):
        task = await session.get(Task, task_id)

        if task is None:
            return None

        task_mapper.mark_done(task)
        await session.flush()

        return task_mapper.to_read(task)

    async def delete_task(
        self,
        session: AsyncSession,
        task_id: int,
    ):
        task = await session.get(Task, task_id)

        if task is None:
            return None

        deleted_task = task_mapper.to_read(task)

        await session.delete(task)
        await session.flush()

        return deleted_task


task_crud = TaskCrud()