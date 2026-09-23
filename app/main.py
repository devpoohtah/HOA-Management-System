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