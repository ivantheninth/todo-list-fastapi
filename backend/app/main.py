from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.tasks import router as tasks_router
from app.core.config import settings

from app.api.routes.chat import router as chat_router

from app.api.routes.health import router as health_router

from app.api.routes.auth import router as auth_router

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

app.include_router(tasks_router)
app.include_router(chat_router)
app.include_router(health_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "App is running"}

