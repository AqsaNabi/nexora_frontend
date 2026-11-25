
import requests
import streamlit as st
import websocket
import json

API_URL = "https://nexora-8xng.onrender.com"
WS_URL = "wss://nexora-8xng.onrender.com"


def api_request(method, endpoint, **kwargs):

    token = st.session_state.get("token")
    headers = kwargs.pop("headers", {})

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return requests.request(
        method,
        f"{API_URL}{endpoint}",
        headers=headers,
        **kwargs
    )


def connect_chat(session_id):

    ws = websocket.create_connection(
        f"{WS_URL}/ws/chat/{session_id}",
        timeout=120
    )

    return ws


def send_chat_message(ws, message):

    ws.send(json.dumps({
        "type": "message",
        "message": message
    }))

    return json.loads(ws.recv())


def approve_job_post(ws):

    ws.send(json.dumps({
        "type": "approve_job_post"
    }))

    return json.loads(ws.recv())


def approve_application_form(ws):

    ws.send(json.dumps({
        "type": "approve_application_form"
    }))

    return json.loads(ws.recv())


def update_drafts(ws, job_post, application_form):

    ws.send(json.dumps({
        "type": "update_drafts",
        "job_post": job_post,
        "application_form": application_form
    }))

    return json.loads(ws.recv())
