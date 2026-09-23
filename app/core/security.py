# app/core/security.py

from typing import Optional

from fastapi import Request

from app.core.config import get_settings
from app.core.supabase_client import get_supabase_client

settings = get_settings()


def get_access_token_from_request(request: Request) -> Optional[str]:
    """
    Reads the Supabase access token out of the session cookie.
    Returns None if no session cookie is present.
    """
    return request.cookies.get(settings.SESSION_COOKIE_NAME)


def get_current_user(request: Request):
    """
    Resolves the currently authenticated user (if any) from the
    session cookie by asking Supabase Auth to validate the token.

    Returns the Supabase user object on success, or None if there
    is no valid session. Does NOT raise — callers decide whether
    an unauthenticated request is allowed to proceed.
    """
    token = get_access_token_from_request(request)
    if not token:
        return None

    supabase = get_supabase_client()

    try:
        response = supabase.auth.get_user(token)
    except Exception:
        return None

    if response is None or response.user is None:
        return None

    return response.user


def is_authenticated(request: Request) -> bool:
    """
    Convenience check: True if the request has a valid Supabase session.
    """
    return get_current_user(request) is not None