import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "claude-sonnet-4-6"
MAX_AGENT_ITERATIONS = 10
MAX_TOKENS = 4096
RANDOM_SEED = 42
NUM_LEADS = 20
NUM_PARTNERS = 30

RISK_CRITICAL_THRESHOLD = 40
RISK_HIGH_THRESHOLD = 60
RISK_MEDIUM_THRESHOLD = 75

UAE_CURRENCY = "AED"
TALABAT_COMMISSION_RATE = 0.15
TALABAT_PLATFORM_FEE = 30


def get_api_key() -> str:
    """Get API key from Streamlit secrets (cloud) or environment (local)."""
    try:
        import streamlit as st
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY", "")
