import json
import uuid
import urllib.parse  # <--- ADDED THIS

import streamlit as st
import websocket
from api import api_request

WEBSOCKET_URL = "ws://127.0.0.1:8000/ws/chat"
REQUEST_TIMEOUT = 600


def initialize_session_state():
    defaults = {
        "session_id": str(uuid.uuid4()),
        "chat_messages": [],
        "current_job_post": {},
        "current_application_form": {},
        "is_approved": False,
        "google_form_url": None,
        "google_form_id": None,
        "recruitment_post_id": None,
        "pending_message": None,
        "page": "job_post_generator",
        "token": None  # <--- MAKE SURE YOUR LOGIN SAVES THE TOKEN HERE
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def send_websocket_event(event):
    ws = None

    try:
        session_id = st.session_state.session_id
        
        # --- CHANGED THIS SECTION ---
        # Get the token from session state and URL-encode it (JWTs have special chars)
        token = st.session_state.get("token")
        safe_token = urllib.parse.quote(token) if token else ""
        
        # Append ?token= to the URL
        ws_url = f"{WEBSOCKET_URL}/{session_id}?token={safe_token}"
        # ----------------------------

        ws = websocket.create_connection(
            ws_url,
            timeout=REQUEST_TIMEOUT
        )

        connection_message = json.loads(ws.recv())

        if connection_message.get("type") != "connected":
            st.error("Unable to establish backend connection.")
            return None

        ws.send(json.dumps(event))
        return json.loads(ws.recv())

    except websocket.WebSocketTimeoutException:
        st.error("The AI response timed out. Please try again.")

    except websocket.WebSocketException:
        st.error("Unable to communicate with the backend.")

    except json.JSONDecodeError:
        st.error("The backend returned an invalid JSON response.")

    except Exception as error:
        st.error(f"Something went wrong: {error}")

    finally:
        if ws is not None:
            try:
                ws.close()
            except Exception:
                pass

    return None


def update_drafts_from_response(response):
    data = response.get("data", response)

    if not isinstance(data, dict):
        return

    job_post = data.get("job_post")
    application_form = data.get("application_form")

    if isinstance(job_post, dict) and isinstance(application_form, dict):
        st.session_state.current_job_post = job_post
        st.session_state.current_application_form = application_form
        st.session_state.is_approved = False
        st.session_state.google_form_url = None
        st.session_state.google_form_id = None
        st.session_state.recruitment_post_id = None


def send_message(message):
    message = message.strip()

    if not message:
        return

    st.session_state.chat_messages.append({
        "role": "user",
        "content": message
    })

    st.session_state.pending_message = message
    st.rerun()


def process_pending_message():
    message = st.session_state.get("pending_message")

    if not message:
        return

    st.session_state.pending_message = None

    with st.spinner("Generating job post..."):
        response = send_websocket_event({
            "type": "message",
            "message": message
        })

        if response is None:
            st.error("No response received from backend.")
            return

        if response.get("type") == "error":
            st.error(response.get("message", "Backend error"))
            return

        data = response.get("data", response)

        if not isinstance(data, dict):
            st.error("Invalid backend response format.")
            return

        if data.get("action") == "draft":
            update_drafts_from_response(data)
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": data.get("message", "Job post generated.")
            })
        else:
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": data.get("message", "Response received.")
            })

    st.rerun()


def approve_both_drafts():
    if not st.session_state.current_job_post:
        st.warning("Please generate a job post before approving.")
        return

    if not st.session_state.current_application_form:
        st.warning("Please generate an application form before approving.")
        return

    with st.spinner("Creating recruitment post and Google Form..."):
        response = send_websocket_event({
            "type": "approve",
            "job_post": st.session_state.current_job_post,
            "application_form": st.session_state.current_application_form
        })

    if not response:
        return

    if response.get("type") == "error":
        st.error(response.get("message", "Approval failed."))
        return

    if response.get("type") in ["approval", "approved"]:
        st.session_state.is_approved = True
        st.session_state.google_form_url = (
            response.get("form_url")
            or response.get("google_form_url")
            or response.get("created_form_url")
        )
        st.session_state.google_form_id = (
            response.get("form_id")
            or response.get("created_form_id")
        )
        st.session_state.recruitment_post_id = (
            response.get("post_id")
            or response.get("created_post_id")
        )
        st.rerun()

    st.error(
        response.get(
            "message",
            "The backend did not confirm approval."
        )
    )


def start_new_job_post():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.chat_messages = []
    st.session_state.current_job_post = {}
    st.session_state.current_application_form = {}
    st.session_state.is_approved = False
    st.session_state.google_form_url = None
    st.session_state.google_form_id = None
    st.session_state.recruitment_post_id = None
    st.session_state.pending_message = None
    st.rerun()