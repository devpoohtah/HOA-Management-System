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
    success = None
    if request.query_params.get("reset") == "success":
        success = "Your password has been updated. Please log in."
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"error": None, "success": success},
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

@router.get("/forgot-password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/forgot_password.html",
        context={"error": None, "sent": False},
    )


@router.post("/forgot-password")
def forgot_password_submit(request: Request, email: str = Form(...)):
    supabase = get_supabase_client()

    try:
        supabase.auth.reset_password_for_email(
            email.strip(),
            {"redirect_to": f"{settings.APP_BASE_URL}/login/reset-password"},
        )
    except Exception as e:
        # Don't leak whether the email exists — log it, but show the
        # same "check your email" message either way.
        print(f"[FORGOT PASSWORD ERROR] {type(e).__name__}: {e}")

    return templates.TemplateResponse(
        request=request,
        name="auth/forgot_password.html",
        context={"error": None, "sent": True},
    )


@router.get("/reset-password")
def reset_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/reset_password.html",
        context={"error": None},
    )


@router.post("/reset-password")
def reset_password_submit(
    request: Request,
    access_token: str = Form(...),
    refresh_token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    if len(new_password) < 8:
        return templates.TemplateResponse(
            request=request,
            name="auth/reset_password.html",
            context={"error": "Password must be at least 8 characters."},
            status_code=400,
        )

    if new_password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="auth/reset_password.html",
            context={"error": "Passwords do not match."},
            status_code=400,
        )

    supabase = get_supabase_client()

    try:
        # The recovery link's token proves identity — establish it as
        # this client's session, then update_user acts on that user.
        supabase.auth.set_session(access_token, refresh_token)
        supabase.auth.update_user({"password": new_password})
    except Exception as e:
        print(f"[RESET PASSWORD ERROR] {type(e).__name__}: {e}")
        return templates.TemplateResponse(
            request=request,
            name="auth/reset_password.html",
            context={"error": "This reset link is invalid or has expired. Please request a new one."},
            status_code=400,
        )

    return RedirectResponse(
        url="/login?reset=success",
        status_code=303,
    )