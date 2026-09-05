from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.crud.task import task_crud
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskRead,
    BulkTaskCreate,
    TaskUpdateAll,
    TaskUpdatePartial,
)


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
async def read_all_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await task_crud.get_all_tasks(
        session=db,
        user_id=current_user.id
    )


@router.get("/{task_id}", response_model=TaskRead)
async def read_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await task_crud.get_task_by_id(
        session=db,
        task_id=task_id,
        user_id=current_user.id,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@router.post("", response_model=TaskRead, status_code=201)
async def create_task_endpoint(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        task = await task_crud.create_task(
            session=db,
            task_data=task_data,
            user_id=current_user.id,
        )

        await db.commit()
        return task

    except Exception:
        await db.rollback()
        raise


@router.post("/bulk", response_model=list[TaskRead], status_code=201)
async def create_tasks_bulk_endpoint(
    bulk_data: BulkTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        tasks = await task_crud.create_tasks_bulk(
            session=db,
            tasks_data=bulk_data.tasks,
            user_id=current_user.id,
        )

        await db.commit()
        return tasks

    except Exception:
        await db.rollback()
        raise


@router.put("/{task_id}", response_model=TaskRead)
async def update_whole_task_endpoint(
    task_id: int,
    task_data: TaskUpdateAll,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await task_crud.update_whole_task(
        session=db,
        task_id=task_id,
        user_id=current_user.id,
        task_data=task_data,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task_partially_endpoint(
    task_id: int,
    task_data: TaskUpdatePartial,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await task_crud.update_task_partially(
        session=db,
        task_id=task_id,
        user_id=current_user.id,
        task_data=task_data,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return task


@router.delete("/{task_id}", response_model=TaskRead)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await task_crud.delete_task(
        session=db,
        task_id=task_id,
        user_id=current_user.id
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return task