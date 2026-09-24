import logging
import time
import uuid

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import metrics

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.tasks import router as tasks_router
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.core.telemetry import configure_tracing


configure_logging()
configure_tracing()

logger = logging.getLogger(__name__)

meter = metrics.get_meter(__name__)

http_requests_total = meter.create_counter(
    name="http_requests_total",
    description="Total number of HTTP requests",
    unit="1",
)

http_request_duration = meter.create_histogram(
    name="http_request_duration_ms",
    description="HTTP request duration in milliseconds",
    unit="ms",
)

app = FastAPI()

FastAPIInstrumentor.instrument_app(app)

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
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)

app.include_router(tasks_router)
app.include_router(chat_router)
app.include_router(health_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "App is running"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4()),
    )

    request.state.request_id = request_id

    started_at = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled error request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        raise

    duration_ms = (
        time.perf_counter() - started_at
    ) * 1000

    http_requests_total.add(
        1,
        {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )

    http_request_duration.record(
        duration_ms,
        {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )

    logger.info(
        "Request completed request_id=%s method=%s "
        "path=%s status=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    response.headers["X-Request-ID"] = request_id
    return response
