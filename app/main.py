# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.templates import templates  # noqa: F401  (imported for app-wide availability)

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

# --- Static files (CSS, JS, images) ---
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Routers ---
from app.routers import (  # noqa: E402
    pages,
    auth,
    homeowners,
    dashboard,
    dues,
    payments,
    expenses,
    announcements,
    complaints,
    projects,
    documents,
    meetings,
    requests,
)

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(homeowners.router)
app.include_router(dashboard.router)
app.include_router(dues.router)
app.include_router(payments.router)
app.include_router(expenses.router)
app.include_router(announcements.router)
app.include_router(complaints.router)
app.include_router(projects.router)
app.include_router(documents.router)
app.include_router(meetings.router)
app.include_router(requests.router)

import logging
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import http_exception_handler

logger = logging.getLogger(__name__)

ERROR_PAGES = {
    404: ("Page Not Found", "The page you're looking for doesn't exist or may have been moved."),
    403: ("Access Denied", "You don't have permission to access this page."),
    500: ("Something Went Wrong", "An unexpected error occurred. Please try again, or contact the HOA office if the problem continues."),
}


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc: StarletteHTTPException):
    if exc.status_code in ERROR_PAGES:
        title, default_message = ERROR_PAGES[exc.status_code]
        detail = exc.detail if isinstance(exc.detail, str) else None
        message = detail if detail and detail != "Not Found" else default_message
        return templates.TemplateResponse(
            request=request,
            name="errors/error.html",
            status_code=exc.status_code,
            context={"status_code": exc.status_code, "title": title, "message": message},
        )
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def custom_server_error_handler(request, exc: Exception):
    logger.exception("Unhandled server error on %s", request.url.path)
    title, message = ERROR_PAGES[500]
    return templates.TemplateResponse(
        request=request,
        name="errors/error.html",
        status_code=500,
        context={"status_code": 500, "title": title, "message": message},
    )