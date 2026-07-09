from fastapi import FastAPI
from database import Base, engine
from schemas import TaskCreate, TaskUpdatePartial, TaskUpdateAll
from crud import task_crud
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:63342",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "App is running"}

@app.get("/tasks")
def read_all_tasks():
    return task_crud.get_all_tasks()

@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    return task_crud.get_task_by_id(task_id)

@app.post("/tasks")
def create_task_endpoint(task_data: TaskCreate):
    return task_crud.create_task(task_data)

@app.put("/tasks/{task_id}")
def update_whole_task_endpoint(task_id: int, task_data: TaskUpdateAll):
    return task_crud.update_whole_task(task_id, task_data)

@app.patch("/tasks/{task_id}")
def update_task_partially_endpoint(task_id: int, task_data: TaskUpdatePartial):
    return task_crud.update_task_partially(task_id, task_data)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    return task_crud.delete_task(task_id)




