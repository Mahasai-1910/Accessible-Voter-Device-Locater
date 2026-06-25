"""Authentication and role-based access control."""

from __future__ import annotations

import hashlib
from typing import Literal

import streamlit as st

Role = Literal["Super Admin", "Election Officer", "Accessibility Coordinator", "Volunteer"]

USERS: dict[str, dict] = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "Super Admin",
        "name": "System Administrator",
    },
    "officer": {
        "password_hash": hashlib.sha256("officer123".encode()).hexdigest(),
        "role": "Election Officer",
        "name": "Election Officer",
    },
    "coordinator": {
        "password_hash": hashlib.sha256("coord123".encode()).hexdigest(),
        "role": "Accessibility Coordinator",
        "name": "Accessibility Coordinator",
    },
    "volunteer": {
        "password_hash": hashlib.sha256("volunteer123".encode()).hexdigest(),
        "role": "Volunteer",
        "name": "Volunteer",
    },
}

ROLE_PERMISSIONS = {
    "Super Admin": {"upload", "manage_locations", "manage_devices", "reports", "admin", "analytics"},
    "Election Officer": {"upload", "manage_locations", "reports", "analytics"},
    "Accessibility Coordinator": {"manage_devices", "reports", "analytics", "matcher"},
    "Volunteer": {"locator", "matcher"},
}


def verify_login(username: str, password: str) -> bool:
    user = USERS.get(username.lower().strip())
    if not user:
        return False
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    if pwd_hash == user["password_hash"]:
        st.session_state.authenticated = True
        st.session_state.username = username.lower().strip()
        st.session_state.role = user["role"]
        st.session_state.user_name = user["name"]
        return True
    return False


def logout() -> None:
    for key in ["authenticated", "username", "role", "user_name"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.authenticated = False


def has_permission(permission: str) -> bool:
    if not st.session_state.get("authenticated"):
        return False
    role = st.session_state.get("role", "")
    return permission in ROLE_PERMISSIONS.get(role, set())


def require_auth(min_role: str | None = None) -> bool:
    if not st.session_state.get("authenticated"):
        return False
    if min_role == "admin" and st.session_state.get("role") != "Super Admin":
        return False
    return True
