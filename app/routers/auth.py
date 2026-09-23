# app/routers/auth.py

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from app.core.templates import templates
from app.core.supabase_client import get_supabase_client
from app.core.config import get_settings

router = APIRouter(prefix="/login", tags=["auth"])
settings = get_settings()


@router.get("")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"error": None},
    )


@router.post("")
def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    supabase = get_supabase_client()

    try:
        result = supabase.auth.sign_in_with_password(
            {"email": email.strip(), "password": password}
        )
    except Exception as e:
        print(f"[LOGIN ERROR] {type(e).__name__}: {e}")  # TEMPORARY — remove once diagnosed
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"error": "Invalid email or password."},
            status_code=401,
        )

    if not result or not result.session:
        print("[LOGIN ERROR] sign_in returned no session, no exception raised")  # TEMPORARY
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"error": "Invalid email or password."},
            status_code=401,
        )

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=result.session.access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
    )
    return response


@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(settings.SESSION_COOKIE_NAME)
    return response