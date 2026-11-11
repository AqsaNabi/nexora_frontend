
import json
import uuid

import streamlit as st
import websocket

from api import api_request
import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from backend.authen.auth import create_token



# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"
WEBSOCKET_URL = "ws://127.0.0.1:8000/ws/chat"

REQUEST_TIMEOUT = 600


# ============================================================
# STYLING
# ============================================================

def apply_styling():

    st.markdown(
        """
        <style>

        .stApp {
            background-color: #f4f7fb;
        }

        .block-container {
            max-width: 1250px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            color: #183B66 !important;
            font-weight: 750 !important;
        }

        hr {
            border-color: #dce5f0 !important;
        }

        /* LEFT SIDEBAR */

        [data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #142D4E 0%,
                #203F68 55%,
                #352D68 100%
            ) !important;

            border-right: 1px solid #304f78 !important;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] .stMarkdown {
            color: white !important;
        }

        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            color: #c6d5eb !important;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.22) !important;
        }

        [data-testid="stSidebar"] div.stButton > button {
            width: 100%;
            min-height: 44px;

            background: linear-gradient(
                135deg,
                #526FE8,
                #7656CE
            ) !important;

            color: white !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
            border-radius: 11px !important;
            font-weight: 650 !important;
        }

        [data-testid="stSidebar"] div.stButton > button:hover {
            background: linear-gradient(
                135deg,
                #718AFF,
                #9575E8
            ) !important;

            border-color: white !important;
        }

        /* MAIN BUTTONS */

        div.stButton > button {
            min-height: 44px;
            border-radius: 10px;
            font-weight: 600;
            border: 1px solid #dce4ef;
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(
                135deg,
                #526FE8,
                #7656CE
            ) !important;

            border: 1px solid #526FE8 !important;
            color: white !important;
        }

        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(
                135deg,
                #718AFF,
                #9575E8
            ) !important;

            color: white !important;
        }

        /* INPUTS */

        div[data-testid="stTextArea"] textarea {
            border-radius: 12px;
            border: 1px solid #dce4ef;
            background-color: white;
            line-height: 1.6;
        }

        /* WELCOME SECTION */

        .welcome-container {
            text-align: center;
            padding: 35px 25px;
            max-width: 850px;
            margin: 0 auto;
        }

        .welcome-heading {
            color: #526FE8;
            font-size: 19px;
            font-weight: 600;
            margin-bottom: 14px;
        }

        .welcome-subheading {
            color: #183B66;
            font-size: 30px;
            font-weight: 750;
            margin-bottom: 15px;
        }

        .welcome-description {
            color: #64748B;
            font-size: 16px;
            line-height: 1.8;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state():

    defaults = {
        "session_id": str(uuid.uuid4()),
        "chat_messages": [],
        "current_job_post": {},
        "current_application_form": {},
        "approved_payload": None,
        "approved_json_path": None,
        "is_approved": False,
        "json_editor_text": "",
        "json_editor_needs_sync": True,
        "page": "job_post_generator",
        "pending_message": None
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# JSON EDITOR
# ============================================================

def get_combined_json():

    return {
        "job_post": st.session_state.current_job_post,
        "application_form": st.session_state.current_application_form
    }


def sync_json_editor():

    if st.session_state.json_editor_needs_sync:

        st.session_state.json_editor_text = json.dumps(
            get_combined_json(),
            indent=4,
            ensure_ascii=False
        )

        st.session_state.json_editor_needs_sync = False


def apply_json_editor_changes():

    try:

        edited_data = json.loads(
            st.session_state.json_editor_text
        )

        if not isinstance(edited_data, dict):
            raise ValueError("The JSON root must be an object.")

        job_post = edited_data.get("job_post")
        application_form = edited_data.get("application_form")

        if not isinstance(job_post, dict):
            raise ValueError("'job_post' must be a JSON object.")

        if not isinstance(application_form, dict):
            raise ValueError(
                "'application_form' must be a JSON object."
            )

        st.session_state.current_job_post = job_post
        st.session_state.current_application_form = application_form

        return True

    except (json.JSONDecodeError, ValueError) as error:

        st.error(f"Invalid JSON: {error}")
        return False


# ============================================================
# WEBSOCKET COMMUNICATION
# ============================================================

def send_websocket_event(event):

    ws = None

    try:

        # Get the existing JWT token from main Nexora login.
        token = st.session_state.get("token")

        if not token:

            st.error(
                "Authentication token not found. Please log in."
            )

            return None

        # Get the current conversation session ID.
        session_id = st.session_state.session_id

        # The current backend expects the token in query parameters.
        ws_url = (
            f"{WEBSOCKET_URL}/{session_id}"
            f"?token={token}"
        )

        # Establish authenticated WebSocket connection.
        ws = websocket.create_connection(
            ws_url,
            timeout=REQUEST_TIMEOUT
        )

        connection_message = json.loads(ws.recv())

        if connection_message.get("type") == "error":

            raise Exception(
                connection_message.get(
                    "message",
                    "WebSocket connection failed."
                )
            )

        # Send event to backend.
        ws.send(json.dumps(event))

        # Receive backend response.
        response = json.loads(ws.recv())

        return response

    except websocket.WebSocketTimeoutException:

        st.error("The AI response timed out. Please try again.")
        return None

    except websocket.WebSocketException as error:

        st.error(f"WebSocket connection error: {error}")
        return None

    except json.JSONDecodeError:

        st.error("The backend returned an invalid response.")
        return None

    except Exception as error:

        st.error(f"Something went wrong: {error}")
        return None

    finally:

        if ws is not None:

            try:
                ws.close()
            except Exception:
                pass


# ============================================================
# RESPONSE HANDLING
# ============================================================

def update_drafts_from_response(response):

    data = response.get("data", response)

    if not isinstance(data, dict):
        return

    job_post = data.get("job_post")
    application_form = data.get("application_form")

    if isinstance(job_post, dict):
        st.session_state.current_job_post = job_post

    if isinstance(application_form, dict):
        st.session_state.current_application_form = application_form

    if (
        isinstance(job_post, dict)
        and isinstance(application_form, dict)
    ):

        st.session_state.json_editor_needs_sync = True
        st.session_state.is_approved = False
        st.session_state.approved_payload = None
        st.session_state.approved_json_path = None


# ============================================================
# SEND MESSAGE
# ============================================================

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


# ============================================================
# PROCESS PENDING MESSAGE
# ============================================================

def process_pending_message(processing_placeholder):

    message = st.session_state.pending_message

    if not message:
        return

    # Clear pending state before processing.
    st.session_state.pending_message = None

    with processing_placeholder.container():

        with st.chat_message("assistant"):

            with st.spinner("Processing your request..."):

                response = send_websocket_event({
                    "type": "message",
                    "message": message
                })

    if not response:

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": (
                "I couldn't process your request. "
                "Please try again."
            )
        })

        st.rerun()

    if response.get("type") == "error":

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response.get(
                "message",
                "I couldn't process that request."
            )
        })

        st.rerun()

    if response.get("type") != "response":

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response.get(
                "message",
                "Unexpected response from the backend."
            )
        })

        st.rerun()

    data = response.get("data", {})

    if not isinstance(data, dict):
        data = {}

    action = data.get("action")

    if action == "answer":

        assistant_message = (
            data.get("answer")
            or "I don't know the answer to that."
        )

    elif action == "draft":

        update_drafts_from_response(response)

        assistant_message = (
            data.get("message")
            or (
                "Your job description and application "
                "form have been generated."
            )
        )

    else:

        update_drafts_from_response(response)

        assistant_message = (
            data.get("message")
            or "Your request has been processed."
        )

    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": assistant_message
    })

    st.rerun()


# ============================================================
# APPROVE BOTH DRAFTS
# ============================================================

def approve_both_drafts():

    if not apply_json_editor_changes():
        return

    if not st.session_state.current_job_post:

        st.warning("There is no job description to approve.")
        return

    if not st.session_state.current_application_form:

        st.warning("There is no application form to approve.")
        return

    with st.spinner("Approving and saving the final JSON..."):

        response = send_websocket_event({
            "type": "approve",
            "job_post": st.session_state.current_job_post,
            "application_form": (
                st.session_state.current_application_form
            )
        })

    if not response:
        return

    if response.get("type") == "error":

        st.error(
            response.get(
                "message",
                "Approval failed."
            )
        )
        return

    if response.get("type") in ["approval", "approved"]:

        st.session_state.is_approved = True

        st.session_state.approved_payload = (
            response.get("approved_payload")
            or response.get("data")
        )

        st.session_state.approved_json_path = (
            response.get("saved_file")
        )

        st.rerun()

    st.error(
        response.get(
            "message",
            "The backend did not confirm approval."
        )
    )


# ============================================================
# START NEW JOB POST
# ============================================================

def start_new_job_post():

    st.session_state.session_id = str(uuid.uuid4())

    st.session_state.chat_messages = []

    st.session_state.current_job_post = {}

    st.session_state.current_application_form = {}

    st.session_state.approved_payload = None

    st.session_state.approved_json_path = None

    st.session_state.is_approved = False

    st.session_state.json_editor_text = ""

    st.session_state.json_editor_needs_sync = True

    st.session_state.pending_message = None

    st.rerun()


# ============================================================
# LEFT SIDEBAR
# ============================================================

def display_sidebar():

    with st.sidebar:

        st.markdown("## HELLO HR!")

        st.caption("HR Department")

        st.divider()

        if st.button(
            "← Back to Main Dashboard",
            key="back_to_dashboard",
            use_container_width=True
        ):

            st.session_state.page = "dashboard"
            st.rerun()

        st.divider()

        st.markdown("### Form Link Generator")

        if st.button(
            "＋ Start New Job Post",
            key="sidebar_new_job",
            use_container_width=True
        ):

            start_new_job_post()


# ============================================================
# CHAT DISPLAY
# ============================================================

def display_chat_messages():

    for message in st.session_state.chat_messages:

        role = message.get("role", "assistant")

        content = message.get("content", "")

        if role not in ["user", "assistant"]:
            continue

        if not content:
            continue

        with st.chat_message(role):

            st.markdown(content)


# ============================================================
# WELCOME SECTION
# ============================================================

def display_welcome_section():

    if st.session_state.chat_messages:
        return

    left_space, center_content, right_space = st.columns(
        [1, 5, 1]
    )

    with center_content:

        st.markdown(
            "<h3 style='text-align:center; color:#526FE8;'>"
            "Let's Get Started!"
            "</h3>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<h2 style='text-align:center; color:#183B66;'>"
            "Your hiring journey starts here."
            "</h2>",
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <p style="
                text-align:center;
                color:#64748B;
                font-size:16px;
                line-height:1.8;
            ">
                Tell us about the position you're hiring for.
                We'll help you create a professional job
                description and candidate application form.
            </p>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# JOB DESCRIPTION AND APPLICATION FORM PREVIEW
# ============================================================

def display_complete_preview():

    job_post = st.session_state.current_job_post

    application_form = (
        st.session_state.current_application_form
    )

    if not job_post or not application_form:
        return

    st.header("Complete Preview")

    st.caption(
        "Review the generated job description and "
        "application form below."
    )

    # --------------------------------------------------
    # 1. JOB DESCRIPTION
    # --------------------------------------------------

    st.subheader("1. Job Description")

    job_description = job_post.get(
        "job_description",
        ""
    )

    if job_description:

        st.markdown(job_description)

    else:

        st.caption("Job description has not been provided.")

    st.divider()

    # --------------------------------------------------
    # 2. APPLICATION FORM
    # --------------------------------------------------

    st.subheader("2. Application Form")

    form_title = application_form.get("form_title")

    if form_title:

        st.markdown(f"**{form_title}**")

    questions = application_form.get("questions", [])

    if isinstance(questions, list):

        for index, question in enumerate(
            questions,
            start=1
        ):

            with st.container(border=True):

                st.markdown(f"**Question {index}**")

                if isinstance(question, dict):

                    st.write(
                        question.get(
                            "question",
                            question.get("field_name", "")
                        )
                    )

                    st.caption(
                        f"Field: {question.get('field_name', '')}"
                    )

                    st.caption(
                        f"Type: {question.get('type', '')}"
                    )

                    st.caption(
                        "Required: "
                        f"{question.get('required', False)}"
                    )

                else:

                    st.write(question)

    else:

        st.json(application_form)


# ============================================================
# COMBINED JSON EDITOR
# ============================================================

def display_json_editor():

    st.divider()

    st.subheader("3. Combined JSON Output")

    st.caption(
        "Review or edit the complete JSON containing "
        "both the job post and application form."
    )

    sync_json_editor()

    st.text_area(
        "Combined JSON",
        key="json_editor_text",
        height=450,
        disabled=st.session_state.is_approved
    )


# ============================================================
# REVIEW SECTION
# ============================================================

def display_review_section():

    if st.session_state.is_approved:

        st.success(
            "Your job description and application form "
            "have been approved successfully!"
        )

        st.info(
            "The approved JSON has been saved to storage."
        )

        return

    if not st.session_state.current_job_post:
        return

    if not st.session_state.current_application_form:
        return

    # 1. Job Description
    # 2. Application Form

    display_complete_preview()

    # 3. Combined JSON Output

    display_json_editor()

    # Final Approval

    st.divider()

    st.subheader("Final Approval")

    if st.button(
        "Approve Job Description & Application Form",
        type="primary",
        use_container_width=True
    ):

        approve_both_drafts()


# ============================================================
# MAIN PAGE - RIGHT SIDE
# ============================================================

def job_post_generator():

   

    initialize_session_state()

    # Temporary token for independent testing
    if not st.session_state.get("token"):
        st.session_state.token = create_token("test@example.com")

    apply_styling()

    

    # LEFT SIDEBAR
    display_sidebar()

    # MAIN DASHBOARD NAVIGATION
    if st.session_state.page == "dashboard":

        st.info(
            "You selected Back to Main Dashboard. "
            "The parent dashboard must handle this navigation."
        )

        return

    # RIGHT MAIN CONTENT
    st.title(
        "💼📑 Job Post – Application Link Generator"
    )

    st.caption(
        "Generate, review and approve job "
        "descriptions and application forms."
    )

    st.divider()

    # CONVERSATION ANCHOR
    st.markdown(
        '<div id="chat-conversation-anchor"></div>',
        unsafe_allow_html=True
    )

    # WELCOME CONTENT
    display_welcome_section()

    # PREVIOUS CONVERSATIONS
    display_chat_messages()

    # PROCESSING PLACEHOLDER
    processing_placeholder = st.empty()

    # PROCESS PENDING MESSAGE
    process_pending_message(processing_placeholder)

    # GENERATED DRAFTS AND APPROVAL
    display_review_section()

    # CHAT INPUT
    if not st.session_state.is_approved:

        user_message = st.chat_input(
            "Describe the job role and enter HR requirements..."
        )

        if user_message:

            send_message(user_message)


if __name__ == "__main__":
    job_post_generator()
