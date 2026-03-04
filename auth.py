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

Login is ephemeral (session-state only), so users re-enter credentials on
page refresh — that's intentional and normal for a lightweight demo.
Email history persists independently via Supabase (storage.py).
"""
from __future__ import annotations

import streamlit as st


def get_current_user() -> str | None:
    """Return the logged-in username, or None if not authenticated."""
    return st.session_state.get("logged_in_user")


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
            # Clear any stale cache from a previous user
            st.session_state.pop("email_history_cache", None)
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
    """Clear auth state and cached history, then rerun."""
    st.session_state.pop("logged_in_user", None)
    st.session_state.pop("email_history_cache", None)
    st.rerun()
