# app/core/supabase_client.py

from functools import lru_cache
from supabase import create_client, Client

from app.core.config import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """
    Standard Supabase client, authenticated with the PUBLISHABLE key
    (low-privilege, replaces the legacy anon key). Respects Row
    Level Security and should be used for the vast majority of
    request-scoped database and auth operations.
    """
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_PUBLISHABLE_KEY)


@lru_cache
def get_supabase_admin_client() -> Client:
    """
    Privileged Supabase client, authenticated with the SECRET key
    (elevated privilege, replaces the legacy service_role key). This
    client BYPASSES Row Level Security entirely.

    Use only for specific, deliberate server-side operations that
    have already been authorized through our own application logic
    (e.g. admin-only actions verified via app.core.dependencies).

    Never expose this client, or data fetched through it, directly
    to a homeowner-facing route without an explicit authorization
    check first.
    """
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SECRET_KEY)


def get_user_scoped_client(access_token: str) -> Client:
    """
    Creates a FRESH (not cached) Supabase client authenticated with
    the publishable key, then re-authed as a specific user's access
    token, so Row Level Security policies are evaluated as that user
    rather than the anonymous/publishable role.

    access_token here is the user's own SESSION token (set at login,
    stored in the session cookie) — unrelated to the publishable/
    secret API keys above. Deliberately not cached with @lru_cache:
    each request may belong to a different homeowner, and caching
    here would risk one user's session leaking into another user's
    request. Use this for any query that must be scoped to "the
    currently logged-in homeowner's own data" (profile, own dues,
    own payments, own complaints, own requests).
    """
    settings = get_settings()
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_PUBLISHABLE_KEY)
    client.postgrest.auth(access_token)
    return client