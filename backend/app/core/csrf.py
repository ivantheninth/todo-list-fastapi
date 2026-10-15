from urllib.parse import urlsplit

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
COOKIE_AUTH_MUTATION_PATHS = {"/auth/login", "/auth/logout"}


def is_valid_origin(origin: str | None) -> bool:
    if not origin or origin == "null":
        return False

    try:
        parsed = urlsplit(origin)
        _ = parsed.port
    except ValueError:
        return False

    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        return False

    return origin == f"{parsed.scheme}://{parsed.netloc}"


def get_trusted_origins() -> set[str]:
    configured_origins = {
        origin.strip()
        for origin in settings.CSRF_TRUSTED_ORIGINS.split(",")
        if origin.strip()
    }

    return {settings.FRONTEND_ORIGIN, *configured_origins}


def is_trusted_origin(origin: str | None) -> bool:
    return is_valid_origin(origin) and origin in get_trusted_origins()


class CSRFCookieAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        has_auth_cookie = settings.AUTH_COOKIE_NAME in request.cookies
        requires_strict_origin = (
            request.method in UNSAFE_METHODS
            and (
                has_auth_cookie
                or request.url.path in COOKIE_AUTH_MUTATION_PATHS
            )
        )

        if requires_strict_origin:
            if not is_trusted_origin(request.headers.get("Origin")):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF validation failed"},
                )

        return await call_next(request)
