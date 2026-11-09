import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


def api_request(method, endpoint, **kwargs):

    token = st.session_state.get("token")

    headers = kwargs.pop("headers", {})

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(
        method,
        f"{API_URL}{endpoint}",
        headers=headers,
        **kwargs
    )

    return response