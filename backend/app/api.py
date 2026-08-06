from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.crud import task_crud
from app.database import Base, engine, get_db
from app.schemas import TaskCreate, TaskUpdateAll, TaskUpdatePartial


Base.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://136.64.109.220:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "App is running"}


@app.get("/tasks")
def read_all_tasks(db: Session = Depends(get_db)):
    return task_crud.get_all_tasks(db)


@app.get("/tasks/{task_id}")
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = task_crud.get_task_by_id(db, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@app.post("/tasks")
def create_task_endpoint(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    try:
        task = task_crud.create_task(db, task_data)
        db.commit()
        return task
    except Exception:
        db.rollback()
        raise


@app.put("/tasks/{task_id}")
def update_whole_task_endpoint(
    task_id: int,
    task_data: TaskUpdateAll,
    db: Session = Depends(get_db),
):
    task = task_crud.update_whole_task(
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
        db.commit()
    except Exception:
        db.rollback()
        raise

    return task


@app.patch("/tasks/{task_id}")
def update_task_partially_endpoint(
    task_id: int,
    task_data: TaskUpdatePartial,
    db: Session = Depends(get_db),
):
    task = task_crud.update_task_partially(
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
        db.commit()
    except Exception:
        db.rollback()
        raise

    return task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = task_crud.delete_task(
        db,
        task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return task
