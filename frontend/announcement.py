import os
import re
import requests
import streamlit as st
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

try:
    from api import api_request, API_URL
except ImportError:
    # Fallback if run standalone outside parent directory
    API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

    def api_request(method, endpoint, **kwargs):
        headers = kwargs.pop("headers", {})
        token = st.session_state.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        return requests.request(
            method,
            f"{API_URL}{endpoint}",
            headers=headers,
            **kwargs,
        )


REQUEST_TIMEOUT = 300


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

        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e5eaf2 !important;
            display: block !important;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #17365d;
        }

        .st-key-announcement_profile_photo img {
            display: block;
        }

        .announcement-profile-details {
            text-align: center;
            color: #17365d;
            overflow-wrap: anywhere;
        }

        .announcement-profile-name {
            font-weight: 700;
            margin-bottom: 4px;
        }

        .announcement-profile-department {
            color: #6b7280;
            font-size: 14px;
        }

        h1 {
            color: #17365d !important;
            font-weight: 800 !important;
        }

        h2, h3 {
            color: #17365d !important;
            font-weight: 700 !important;
        }

        div.stButton > button {
            min-height: 44px;
            border-radius: 10px;
            font-weight: 600;
        }

        div.stButton > button[kind="primary"] {
            background-color: #FF4B4B !important;
            border: 1px solid #FF4B4B !important;
            color: white !important;
        }

        div.stButton > button[kind="primary"]:hover {
            background-color: #D32F2F !important;
            border-color: #D32F2F !important;
            color: white !important;
        }

        div.stButton > button[kind="primary"]:focus,
        div.stButton > button[kind="primary"]:active {
            background-color: #B71C1C !important;
            border-color: #B71C1C !important;
            color: white !important;
            box-shadow: 0 0 0 0.2rem rgba(255, 75, 75, 0.25) !important;
        }

        div[data-testid="stTextInput"] input {
            border-radius: 10px;
            border: 1px solid #dce4ef;
            background-color: white;
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 12px;
            border: 1px solid #dce4ef;
            background-color: white;
            line-height: 1.6;
        }

        hr {
            border-color: #e2e8f0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


DEFAULT_STATE = {
    "audience": "All Employees",
    "prompt": "",
    "announcement_title": "",
    "announcement_body": "",
    "modify_prompt": "",
    "status": "Not generated",
    "technical_error": "",
    "notification": "",
    "notification_type": "info",
}


def init_session_state():
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def notify(message, notification_type="info"):
    st.session_state.notification = message
    st.session_state.notification_type = notification_type


def show_notification():
    message = st.session_state.notification
    if not message:
        return

    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
    }

    st.toast(
        message,
        icon=icons.get(st.session_state.notification_type, "ℹ️"),
    )
    st.session_state.notification = ""


def extract_model_text(data):
    """
    Extracts the clean announcement text from backend response,
    filtering out any Gemini/Gemma 'thinking' blocks completely.
    """
    if not isinstance(data, dict):
        return ""

    raw_announcement = (
        data.get("announcement")
        or data.get("generated_announcement")
        or data.get("content")
        or ""
    )

    if isinstance(raw_announcement, str):
        return raw_announcement.strip()

    if isinstance(raw_announcement, list):
        text_parts = []

        for item in raw_announcement:
            if isinstance(item, dict):
                if item.get("type") == "thinking":
                    continue

                if "text" in item:
                    text_parts.append(str(item["text"]).strip())
                elif item.get("type") == "text":
                    text_parts.append(str(item.get("content", "")).strip())

            elif isinstance(item, str):
                text_parts.append(item.strip())

        if text_parts:
            return "\n\n".join(text_parts).strip()

    return str(raw_announcement).strip()


def extract_title_and_content(response_text):
    """
    Parses TITLE and ANNOUNCEMENT content safely.
    Guarantees no '[Title]', '[Content]', '\\n' or placeholder tokens leak.
    """
    response_text = str(response_text).strip()
    if not response_text:
        return "", ""

    placeholder_pattern = re.compile(
        r"TITLE\s*:\s*\[Title\]",
        re.IGNORECASE,
    )

    if placeholder_pattern.search(response_text):
        return "", ""

    title_match = re.search(
        r"TITLE\s*:\s*(.*?)(?=\n\s*ANNOUNCEMENT\s*:)",
        response_text,
        re.IGNORECASE | re.DOTALL,
    )

    content_match = re.search(
        r"ANNOUNCEMENT\s*:\s*(.*)",
        response_text,
        re.IGNORECASE | re.DOTALL,
    )

    if title_match:
        title = title_match.group(1).strip()
    else:
        lines = response_text.split("\n", 1)
        first_line = lines[0]

        if first_line.upper().startswith("TITLE:"):
            title = first_line.split(":", 1)[1].strip()
        else:
            title = ""

    if content_match:
        content = content_match.group(1).strip()
    else:
        content = response_text

    title = re.sub(r"\[.*?\]", "", title)
    title = title.replace("\\n", " ").replace("\n", " ").strip()
    title = " ".join(title.split())

    content = re.sub(
        r"^\s*TITLE\s*:.*?(?=\n)",
        "",
        content,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    ).strip()

    content = re.sub(
        r"^\s*ANNOUNCEMENT\s*:\s*",
        "",
        content,
        count=1,
        flags=re.IGNORECASE,
    ).strip()

    content = re.sub(
        r"\[Content\]|\[Title\]",
        "",
        content,
        flags=re.IGNORECASE,
    )
    content = re.sub(r"\n{3,}", "\n\n", content)

    if not title:
        title = "Company Announcement"

    return title, content


def call_api(endpoint, payload):
    try:
        response = api_request(
            "POST",
            endpoint,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        try:
            data = response.json()
        except ValueError:
            data = {"detail": response.text}

        if response.status_code >= 400:
            return None, str(
                data.get("detail", f"HTTP error {response.status_code}")
            )

        return data, None

    except requests.exceptions.ConnectionError:
        return None, (
            f"Cannot connect to FastAPI backend at {API_URL}. "
            "Please ensure your backend server is running."
        )

    except requests.exceptions.Timeout:
        return None, (
            f"Request timed out after {REQUEST_TIMEOUT} seconds. "
            "The model is taking longer to respond. Please try again."
        )

    except requests.exceptions.RequestException as error:
        return None, str(error)


def generate_announcement():
    prompt = st.session_state.prompt.strip()
    audience = st.session_state.audience

    if not prompt:
        notify("Please enter announcement instructions.", "warning")
        return

    payload = {
        "designation": audience,
        "prompt": prompt,
    }

    st.session_state.technical_error = ""

    with st.spinner("Generating announcement with AI... Please wait."):
        data, error = call_api("/announcements/generate", payload)

    if error:
        st.session_state.technical_error = error
        notify("Announcement generation failed.", "error")
        return

    response_text = extract_model_text(data)
    if not response_text:
        notify("No announcement content received from AI.", "warning")
        return

    title, content = extract_title_and_content(response_text)

    st.session_state.announcement_title = title
    st.session_state.announcement_body = content
    st.session_state.status = "Awaiting approval"
    st.session_state.modify_prompt = ""

    notify("Announcement generated successfully.", "success")


def modify_announcement():
    instruction = st.session_state.modify_prompt.strip()
    title = st.session_state.announcement_title.strip()
    content = st.session_state.announcement_body.strip()

    if not instruction:
        notify("Please describe the changes you want.", "warning")
        return

    if not content:
        notify("Generate an announcement first before modifying.", "warning")
        return

    existing_announcement = (
        f"TITLE: {title}\n\n"
        f"ANNOUNCEMENT:\n\n"
        f"{content}"
    )

    payload = {
        "designation": st.session_state.audience,
        "existing_announcement": existing_announcement,
        "modification_prompt": instruction,
    }

    st.session_state.technical_error = ""

    with st.spinner("Updating announcement with AI... Please wait."):
        data, error = call_api("/announcements/modify", payload)

    if error:
        st.session_state.technical_error = error
        notify("Announcement modification failed.", "error")
        return

    response_text = extract_model_text(data)
    if not response_text:
        notify("No updated announcement received from AI.", "warning")
        return

    updated_title, updated_content = extract_title_and_content(response_text)

    st.session_state.announcement_title = updated_title or title
    st.session_state.announcement_body = updated_content or content
    st.session_state.status = "Awaiting approval"
    st.session_state.modify_prompt = ""

    notify("Announcement updated successfully.", "success")


def approve_announcement():
    title = st.session_state.announcement_title.strip()
    content = st.session_state.announcement_body.strip()

    if not title:
        notify("Announcement title is required.", "warning")
        return

    if not content:
        notify("Announcement content cannot be empty.", "warning")
        return

    payload = {
        "designation": st.session_state.audience,
        "title": title,
        "announcement": content,
    }

    st.session_state.technical_error = ""

    with st.spinner("Saving announcement and sending emails... Please wait."):
        data, error = call_api("/announcements/approve", payload)

    if error:
        st.session_state.technical_error = error
        notify("Announcement approval failed.", "error")
        return

    if data.get("status") == "approved":
        st.session_state.status = "Approved"

        emails_sent = data.get("emails_sent", 0)
        recipients = data.get("total_recipients", 0)
        failed = data.get("emails_failed", 0)

        if failed:
            notify(
                f"Approved! Sent to {emails_sent}/{recipients} recipients ({failed} failed).",
                "warning",
            )
        else:
            notify(
                f"🎉 Announcement approved! Sent to all {emails_sent} recipients.",
                "success",
            )
    else:
        notify("Please check the approval response.", "warning")


def reject_announcement():
    content = st.session_state.announcement_body.strip()
    title = st.session_state.announcement_title.strip() or "Company Announcement"

    if not content:
        notify("There is no announcement to reject.", "warning")
        return

    payload = {
        "designation": st.session_state.audience,
        "title": title,
        "announcement": content,
    }

    st.session_state.technical_error = ""

    with st.spinner("Rejecting announcement... Please wait."):
        data, error = call_api("/announcements/reject", payload)

    if error:
        st.session_state.technical_error = error
        notify("Announcement rejection failed.", "error")
        return

    st.session_state.status = "Rejected"
    st.session_state.announcement_title = ""
    st.session_state.announcement_body = ""
    st.session_state.modify_prompt = ""

    notify("Announcement rejected.", "info")


def reset_announcement():
    st.session_state.prompt = ""
    st.session_state.announcement_title = ""
    st.session_state.announcement_body = ""
    st.session_state.modify_prompt = ""
    st.session_state.status = "Not generated"
    st.session_state.technical_error = ""

    notify("Started a fresh announcement.", "info")
    st.rerun()


def announcement():
    init_session_state()
    apply_styling()

    # Sidebar
    with st.sidebar:
        if st.button(
            "← Back to Dashboard",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.page = "dashboard"
            st.rerun()

        st.divider()

        profile_picture = st.session_state.get("profile_picture")
        full_name = st.session_state.get("full_name") or "HR Administrator"

        if profile_picture:
            with st.container(
                key="announcement_profile_photo",
                horizontal=True,
                horizontal_alignment="center",
            ):
                st.image(profile_picture, width=100)
        else:
            st.html("""
                <div style="
                    display: flex;
                    justify-content: center;
                    margin-bottom: 8px;
                ">
                    <div style="
                        width: 70px;
                        height: 70px;
                        border-radius: 50%;
                        background: #17365d;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 32px;
                    ">
                        👤
                    </div>
                </div>
            """)

        # Use native Markdown for the name and center it with a keyed container.
        with st.container(key="announcement_profile_details"):
            st.markdown(
                """
                <style>
                .st-key-announcement_profile_details {
                    text-align: center;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            st.write(f"**{full_name}**")
            st.caption("HR Department")

        st.divider()

        st.markdown("### Target audience")
        st.selectbox(
            "Recipients",
            [
                "Employee",
                "Manager",
                "Team Lead",
            ],
            key="audience",
            label_visibility="collapsed",
        )

        st.caption(
            "Select the employee group that should receive the announcement."
        )

        st.divider()

        if st.button(
            "＋ New Announcement",
            type="primary",
            use_container_width=True,
        ):
            reset_announcement()

    # Main header
    st.caption("HR WORKSPACE")
    st.title(" Nexora Assistant")
    st.write(
        "Create professional announcements, review AI-generated content, "
        "and communicate with your employees."
    )

    st.caption(f"Selected audience: **{st.session_state.audience}**")

    show_notification()
    st.divider()

    # Technical error display
    if st.session_state.technical_error:
        with st.expander("⚠️ Technical details", expanded=False):
            st.code(st.session_state.technical_error)

    # Create announcement
    st.caption("STEP 01")
    st.subheader("Create announcement")
    st.write("Describe the announcement you want AI to prepare.")

    st.text_area(
        "Announcement instructions",
        key="prompt",
        height=140,
        placeholder=(
            "Example: Generate an announcement for the upcoming quarterly review "
            "of all teams at director room on Friday at 4 PM. Include agenda, "
            "venue, and clear instructions."
        ),
    )

    st.button(
        " Generate announcement",
        type="primary",
        use_container_width=True,
        on_click=generate_announcement,
    )

    # Review announcement
    if st.session_state.announcement_body:
        st.divider()

        st.caption("STEP 02")
        st.subheader("Review announcement")
        st.info(f"Target audience: **{st.session_state.audience}**")

        with st.container(border=True):
            st.markdown("### 📝 Announcement preview")

            st.text_input(
                "Announcement Title (Email Subject)",
                key="announcement_title",
            )

            st.text_area(
                "Announcement Content (Email Body)",
                key="announcement_body",
                height=280,
            )

        # Modify with AI
        st.divider()

        st.caption("STEP 03")
        st.subheader("Modify announcement")
        st.write("Tell AI what you want to adjust or refine.")

        with st.container(border=True):
            st.text_area(
                "Tell AI what to change",
                key="modify_prompt",
                height=100,
                placeholder=(
                    "Example: Make the announcement shorter, add a reminder to "
                    "bring presentation slides, and use an encouraging tone."
                ),
            )

            st.button(
                "🔄 Update announcement",
                use_container_width=True,
                on_click=modify_announcement,
            )

        # Approval and distribution
        st.divider()

        st.caption("STEP 04")
        st.subheader("HR approval")
        st.write(
            "Approve the announcement to save it to the database and dispatch "
            "emails to all selected recipients, or reject the current draft."
        )

        is_approved = st.session_state.status == "Approved"
        approve_col, reject_col = st.columns(2)

        with approve_col:
            st.button(
                "✅ Approve & distribute",
                type="primary",
                use_container_width=True,
                on_click=approve_announcement,
                disabled=is_approved,
            )

        with reject_col:
            st.button(
                "❌ Reject draft",
                use_container_width=True,
                on_click=reject_announcement,
                disabled=is_approved,
            )

        if is_approved:
            st.success(
                "✅ This announcement has been approved and distributed. "
                "No further changes can be made."
            )

    # Workflow status
    st.divider()
    st.subheader("Announcement status")

    status_descriptions = {
        "Not generated": "Enter instructions above and click Generate to begin.",
        "Awaiting approval": "The announcement draft is ready for HR review and approval.",
        "Approved": "The announcement has been approved and distributed via email.",
        "Rejected": "The announcement draft was rejected. You can create a new one.",
    }

    st.markdown(f"**Status: {st.session_state.status}**")
    st.caption(status_descriptions.get(st.session_state.status, ""))

    # Footer
    st.divider()
    st.caption("Nexora HR Automation | Internal Announcement Studio")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Nexora | Announcement Studio",
        page_icon="📢",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    announcement()