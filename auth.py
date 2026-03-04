"""
Authentication for the talabat Partner Intelligence demo.

Users are defined entirely in Streamlit secrets — no code changes needed
to add or remove users. Example secrets.toml entry:

    [users.alice]
    password     = "choose_a_password"
    display_name = "Alice"

    [users.bob]
    password     = "choose_a_password"
    display_name = "Bob"

    [users.carol]           # ← adding a 3rd user is this simple
    password     = "another_password"
    display_name = "Carol"

Login is persisted via a browser cookie (streamlit-cookies-controller) so
users remain logged in across page refreshes. Email and onboarding plan
history persist independently via Supabase (storage.py).
"""
from __future__ import annotations

import streamlit as st
from streamlit_cookies_controller import CookieController

_COOKIE_KEY = "tpi_user"


@st.cache_resource
def _cookie_controller() -> CookieController:
    """Singleton CookieController (one per server process)."""
    return CookieController()


def get_current_user() -> str | None:
    """Return the logged-in username, or None if not authenticated.

    Checks session state first (fast path), then falls back to the
    persisted cookie so users stay logged in after a page refresh.
    """
    # Fast path — already in this session
    if "logged_in_user" in st.session_state:
        return st.session_state["logged_in_user"]

    # Cookie path — restore from a previous session / page refresh
    try:
        saved = _cookie_controller().get(_COOKIE_KEY)
        if saved:
            st.session_state["logged_in_user"] = saved
            return saved
    except Exception:
        pass  # Cookie library not ready yet — will be set on next rerun

    return None


def show_login_form() -> None:
    """Render the login form. Sets ``st.session_state.logged_in_user`` on success."""
    st.markdown("## 🔐 Sign in")
    st.markdown("Enter your credentials to access the Partner Intelligence platform.")
    st.markdown("")

    # Read user list dynamically from secrets — add [users.X] to secrets to onboard new users
    available_users = list(st.secrets.get("users", {}).keys())
    username = st.selectbox("Username", available_users if available_users else ["alice", "bob"])
    password = st.text_input("Password", type="password", placeholder="Enter password…")

    if st.button("Sign in", type="primary", use_container_width=True):
        users_cfg = st.secrets.get("users", {})
        expected = users_cfg.get(username, {}).get("password", "")
        if expected and password == expected:
            st.session_state.logged_in_user = username
            # Persist across page refreshes
            try:
                _cookie_controller().set(_COOKIE_KEY, username)
            except Exception:
                pass
            # Clear any stale cache from a previous user
            st.session_state.pop("email_history_cache", None)
            st.session_state.pop("onboarding_plan_cache", None)
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")


def get_display_name(username: str) -> str:
    """Return the friendly display name for *username* (falls back to capitalised username)."""
    try:
        return st.secrets["users"][username].get("display_name", username.capitalize())
    except Exception:
        return username.capitalize()


def logout() -> None:
    """Clear auth state, cookie, and all caches, then rerun."""
    try:
        _cookie_controller().remove(_COOKIE_KEY)
    except Exception:
        pass
    st.session_state.pop("logged_in_user", None)
    st.session_state.pop("email_history_cache", None)
    st.session_state.pop("onboarding_plan_cache", None)
    st.rerun()
