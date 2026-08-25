from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.crud import task_crud
from app.database import get_db
from app.schemas import TaskCreate, BulkTaskCreate, TaskUpdateAll, TaskUpdatePartial, ChatRequest, ChatResponse
from app.services.llm import llm_service

from app.core.config import settings

from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
    allow_headers=["Content-Type"],
)


@app.get("/")
def root():
    return {"message": "App is running"}


@app.get("/tasks")
async def read_all_tasks(db: AsyncSession = Depends(get_db)):
    return await task_crud.get_all_tasks(db)


@app.get("/tasks/{task_id}")
async def read_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await task_crud.get_task_by_id(db, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@app.post("/tasks")
async def create_task_endpoint(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        task = await task_crud.create_task(db, task_data)
        await db.commit()
        return task
    except Exception:
        await db.rollback()
        raise

@app.post("/tasks/bulk")
async def create_tasks_bulk_endpoint(
    bulk_data: BulkTaskCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        tasks = await task_crud.create_tasks_bulk(
            db,
            bulk_data.tasks,
        )

        await db.commit()

        return tasks

    except Exception:
        await db.rollback()
        raise

@app.put("/tasks/{task_id}")
async def update_whole_task_endpoint(
    task_id: int,
    task_data: TaskUpdateAll,
    db: AsyncSession = Depends(get_db),
):
    task = await task_crud.update_whole_task(
        db,
        task_id,
        task_data,
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


@app.patch("/tasks/{task_id}")
async def update_task_partially_endpoint(
    task_id: int,
    task_data: TaskUpdatePartial,
    db: AsyncSession = Depends(get_db),
):
    task = await task_crud.update_task_partially(
        db,
        task_id,
        task_data,
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


@app.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    task = await task_crud.delete_task(
        db,
        task_id,
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

@app.post("/chat", response_model=ChatResponse)
async def chat(user_request: ChatRequest):
    try:
         return await llm_service.ask(user_request.message)

    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="LLM service is temporarily unavailable",
        )

