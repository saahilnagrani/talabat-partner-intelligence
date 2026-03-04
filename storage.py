"""
Supabase-backed persistent storage for the talabat Partner Intelligence demo.

Tables DDL (run once in Supabase SQL editor):

    CREATE TABLE email_history (
      id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
      user_id     text NOT NULL,
      email_data  jsonb NOT NULL,
      timestamp   timestamptz NOT NULL,
      source      text NOT NULL
    );
    ALTER TABLE email_history DISABLE ROW LEVEL SECURITY;

    CREATE TABLE onboarding_plans (
      id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
      user_id     text NOT NULL,
      partner_id  text NOT NULL,
      plan_data   jsonb NOT NULL,
      timestamp   timestamptz NOT NULL
    );
    ALTER TABLE onboarding_plans DISABLE ROW LEVEL SECURITY;
"""
from __future__ import annotations
from datetime import datetime

import streamlit as st
from supabase import create_client, Client


def _set_error(msg: str) -> None:
    """Store a Supabase error message in session state so the UI can surface it."""
    st.session_state["_supabase_error"] = msg


def _clear_error() -> None:
    st.session_state.pop("_supabase_error", None)


@st.cache_resource
def _get_client() -> Client:
    """Return a singleton Supabase client (cached for the lifetime of the server process)."""
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_ANON_KEY"],
    )


# ---------------------------------------------------------------------------
# Email history
# ---------------------------------------------------------------------------

def load_history(user_id: str) -> list[dict]:
    """Fetch all email history rows for *user_id*, newest first."""
    try:
        res = (
            _get_client()
            .table("email_history")
            .select("*")
            .eq("user_id", user_id)
            .order("timestamp", desc=True)
            .execute()
        )
        rows = res.data or []
        _clear_error()
        return [
            {
                "email": r["email_data"],
                "timestamp": datetime.fromisoformat(r["timestamp"]),
                "source": r["source"],
            }
            for r in rows
        ]
    except Exception as e:
        _set_error(f"load_history failed: {e}")
        return []


def save_email(user_id: str, email: dict, source: str, timestamp: datetime) -> None:
    """Insert one generated email into Supabase."""
    try:
        _get_client().table("email_history").insert(
            {
                "user_id": user_id,
                "email_data": email,
                "timestamp": timestamp.isoformat(),
                "source": source,
            }
        ).execute()
        _clear_error()
    except Exception as e:
        _set_error(f"save_email failed: {e}")


def clear_history(user_id: str) -> None:
    """Delete all email history rows for *user_id*."""
    try:
        _get_client().table("email_history").delete().eq("user_id", user_id).execute()
        _clear_error()
    except Exception as e:
        _set_error(f"clear_history failed: {e}")


# ---------------------------------------------------------------------------
# Onboarding plan persistence
# ---------------------------------------------------------------------------

def load_onboarding_plans(user_id: str) -> list[dict]:
    """Fetch all onboarding plans for *user_id*, newest first."""
    try:
        res = (
            _get_client()
            .table("onboarding_plans")
            .select("*")
            .eq("user_id", user_id)
            .order("timestamp", desc=True)
            .execute()
        )
        rows = res.data or []
        _clear_error()
        return [
            {
                "plan": r["plan_data"],
                "partner_id": r["partner_id"],
                "timestamp": datetime.fromisoformat(r["timestamp"]),
            }
            for r in rows
        ]
    except Exception as e:
        _set_error(f"load_onboarding_plans failed: {e}")
        return []


def save_onboarding_plan(user_id: str, partner_id: str, plan: dict, timestamp: datetime) -> None:
    """Insert one onboarding plan into Supabase."""
    try:
        _get_client().table("onboarding_plans").insert(
            {
                "user_id": user_id,
                "partner_id": partner_id,
                "plan_data": plan,
                "timestamp": timestamp.isoformat(),
            }
        ).execute()
        _clear_error()
    except Exception as e:
        _set_error(f"save_onboarding_plan failed: {e}")


def clear_onboarding_plans(user_id: str) -> None:
    """Delete all onboarding plans for *user_id*."""
    try:
        _get_client().table("onboarding_plans").delete().eq("user_id", user_id).execute()
        _clear_error()
    except Exception as e:
        _set_error(f"clear_onboarding_plans failed: {e}")
