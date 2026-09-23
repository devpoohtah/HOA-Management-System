# app/core/roles.py

"""
Central definition of HOA roles.

Roles are stored in the database (homeowners.role), NOT in Supabase
Auth app_metadata — this lets an admin reassign the role dynamically
(e.g. after an HOA election) through ordinary app CRUD, without
needing to call Supabase's admin auth API.

Only two roles exist right now, per the spec's "do not assume future
role permissions" instruction. ROLE_HIERARCHY is kept as a dict
(rather than a flat equality check) purely so a future role could be
slotted in later without restructuring app.core.dependencies or any
route that calls require_role() — not because a third role is
planned now.
"""

ROLE_HOMEOWNER = "homeowner"
ROLE_ADMIN = "admin"

ROLE_HIERARCHY = {
    ROLE_HOMEOWNER: 0,
    ROLE_ADMIN: 1,
}

ALL_ROLES = list(ROLE_HIERARCHY.keys())


def role_meets_minimum(role: str, minimum_role: str) -> bool:
    """
    True if `role` is at or above `minimum_role`. An unrecognized
    role fails closed (returns False) rather than raising.
    """
    role_level = ROLE_HIERARCHY.get(role)
    minimum_level = ROLE_HIERARCHY.get(minimum_role)

    if role_level is None or minimum_level is None:
        return False

    return role_level >= minimum_level