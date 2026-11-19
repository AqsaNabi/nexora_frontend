import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Search and load .env from multiple potential locations
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)

# Try loading from frontend folder first, then parent folder
load_dotenv(os.path.join(_current_dir, ".env"))
load_dotenv(os.path.join(_parent_dir, ".env"))
load_dotenv()  # Fallback to current working directory

# Single source of truth for the backend base URL
API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def get_api_url(endpoint: str = "") -> str:
    """
    Returns the full backend URL for a given endpoint.
    Ensures leading slash format.
    """
    if endpoint and not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    return f"{API_URL}{endpoint}"


def api_request(method: str, endpoint: str, **kwargs) -> requests.Response:
    """
    Central HTTP request helper for Salif Backend.
    Automatically:
    - Prepends the configured backend API_URL from .env
    - Attaches the JWT Bearer token from st.session_state.token (set at login)
    - Leaves custom headers intact
    """
    headers = kwargs.pop("headers", {})
    if headers is None:
        headers = {}
    else:
        headers = dict(headers)

    # Attach JWT token if authenticated
    token = st.session_state.get("token")
    if token and "Authorization" not in headers:
        headers["Authorization"] = f"Bearer {token}"

    full_url = get_api_url(endpoint)

    return requests.request(
        method=method,
        url=full_url,
        headers=headers,
        **kwargs,
    )
