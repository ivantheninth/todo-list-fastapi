from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.mappers.task import task_mapper
from app.db.models.task import Task
from app.schemas.task import TaskCreate, TaskRead, TaskUpdateAll, TaskUpdatePartial


class TaskCrud:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    async def _get_task_model(
            self,
            session: AsyncSession,
            task_id: int,
            user_id: int,
    ) -> Task | None:

        result = await session.execute(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def create_task(
        self,
        session: AsyncSession,
        task_data: TaskCreate,
        user_id: int
    ) -> TaskRead:

        task = task_mapper.to_model(task_data)
        task.user_id = user_id

        session.add(task)
        await session.flush()

        return task_mapper.to_read(task)

    async def create_tasks_bulk(
            self,
            session: AsyncSession,
            tasks_data: list[TaskCreate],
            user_id: int,
    ) -> list[TaskRead]:

        created_tasks = []

        for task_data in tasks_data:
            task = await self.create_task(
                session=session,
                task_data=task_data,
                user_id=user_id,
            )

            created_tasks.append(task)

        return created_tasks

    async def update_whole_task(
        self,
        session: AsyncSession,
        user_id: int,
        task_id: int,
        task_data: TaskUpdateAll,
    ) -> TaskRead | None:

        task = await self._get_task_model(
            session=session,
            user_id=user_id,
            task_id=task_id,
        )

        if task is None:
            return None

        task_mapper.update_model(task, task_data)
        await session.flush()

        return task_mapper.to_read(task)

    async def update_task_partially(
        self,
        session: AsyncSession,
        user_id: int,
        task_id: int,
        task_data: TaskUpdatePartial,
    ) -> TaskRead | None:

        task = await self._get_task_model(
            session=session,
            user_id=user_id,
            task_id=task_id,
        )

        if task is None:
            return None

        task_mapper.patch_model(task, task_data)
        await session.flush()

        return task_mapper.to_read(task)

    async def get_all_tasks(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[TaskRead]:

        result = await session.execute(
            select(Task).where(Task.user_id == user_id)
        )

        tasks = result.scalars().all()

        return [
            task_mapper.to_read(task)
            for task in tasks
        ]

    async def get_task_by_id(
        self,
        session: AsyncSession,
        user_id: int,
        task_id: int,
    ) -> TaskRead | None:

        task = await self._get_task_model(
            session=session,
            user_id=user_id,
            task_id=task_id,
        )

        if task is None:
            return None

        return task_mapper.to_read(task)

    async def delete_task(
        self,
        session: AsyncSession,
        task_id: int,
        user_id: int,
    ) -> TaskRead | None:

        task = await self._get_task_model(
            session=session,
            user_id=user_id,
            task_id=task_id,
        )

        if task is None:
            return None

        deleted_task = task_mapper.to_read(task)

        await session.delete(task)
        await session.flush()

        return deleted_task


task_crud = TaskCrud()