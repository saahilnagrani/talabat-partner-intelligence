"""
Supabase-backed persistent email history for the talabat Partner Intelligence demo.

Table DDL (run once in Supabase SQL editor):
    CREATE TABLE email_history (
      id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
      user_id     text NOT NULL,
      email_data  jsonb NOT NULL,
      timestamp   timestamptz NOT NULL,
      source      text NOT NULL
    );
"""
from __future__ import annotations
from datetime import datetime

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def _get_client() -> Client:
    """Return a singleton Supabase client (cached for the lifetime of the server process)."""
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_ANON_KEY"],
    )


def load_history(user_id: str) -> list[dict]:
    """Fetch all email history rows for *user_id*, newest first.

    Returns a list of dicts with keys: email (dict), timestamp (datetime), source (str).
    Returns [] on any error so the app degrades gracefully.
    """
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
        return [
            {
                "email": r["email_data"],
                "timestamp": datetime.fromisoformat(r["timestamp"]),
                "source": r["source"],
            }
            for r in rows
        ]
    except Exception:
        return []


def save_email(user_id: str, email: dict, source: str, timestamp: datetime) -> None:
    """Insert one generated email into Supabase. Fails silently (demo app)."""
    try:
        _get_client().table("email_history").insert(
            {
                "user_id": user_id,
                "email_data": email,
                "timestamp": timestamp.isoformat(),
                "source": source,
            }
        ).execute()
    except Exception:
        pass


def clear_history(user_id: str) -> None:
    """Delete all email history rows for *user_id*. Fails silently (demo app)."""
    try:
        _get_client().table("email_history").delete().eq("user_id", user_id).execute()
    except Exception:
        pass
