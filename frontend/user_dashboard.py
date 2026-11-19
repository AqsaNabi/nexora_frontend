import html
from urllib.parse import urlencode

import streamlit as st

from api import api_request


ANNOUNCEMENTS_ENDPOINT = "/announcements/latest"
POLICY_ASK_ENDPOINT = "/user/policies/ask"


def _apply_styles():
    st.html("""
        <style>
        .stApp {
            background: #F4F7FB;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 100%;
        }

        [data-testid="stSidebar"] {
            background: #17365D;
            border-right: none;
        }

        [data-testid="stSidebarContent"] {
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow-y: auto;
        }

        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarUserContent"] [data-testid="stLayoutWrapper"]:has(.st-key-employee_sign_out),
        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"]:has(.st-key-employee_sign_out) {
            display: flex;
            flex-direction: column;
            flex: 1 0 auto;
        }

        .employee-sidebar-title {
            margin: 0;
            padding: 0 0 8px;
            color: #FFFFFF;
            text-align: center;
            font-size: 21px;
            font-weight: 700;
        }

        .st-key-employee_profile_photo [data-testid="stImage"] img {
            display: block;
            width: 112px;
            height: 112px;
            object-fit: cover;
            border-radius: 50%;
            border: 3px solid rgba(255, 255, 255, 0.28);
        }

        .employee-profile {
            text-align: center;
            overflow-wrap: anywhere;
        }

        .employee-profile-name {
            color: #FFFFFF;
            font-size: 17px;
            font-weight: 700;
        }

        .employee-profile-designation {
            color: #DBE7F5;
            font-size: 13px;
            margin-top: 4px;
        }

       [data-testid="stSidebarContent"] [data-testid="stSidebarUserContent"] {
    padding-bottom: 5rem;
}

[data-testid="stSidebarContent"] .st-key-employee_sign_out {
    position: absolute;
    inset-inline: 1rem;
    bottom: 1rem;
    width: auto !important;
}

        .st-key-employee_sign_out button {
            background: #FF4B4B;
            border-color: #FF4B4B;
            color: #FFFFFF;
            border-radius: 10px;
            font-weight: 600;
        }

        .st-key-employee_sign_out button:hover {
            background: #E53838;
            border-color: #E53838;
            color: #FFFFFF;
        }

        .welcome-banner {
            background: linear-gradient(120deg, #17365D, #3730A3, #5148C9);
            padding: 24px 28px;
            border-radius: 14px;
            color: #FFFFFF;
            margin-bottom: 22px;
            box-shadow: 0 4px 16px rgba(32, 38, 94, 0.12);
        }

        .welcome-banner h2 {
            color: #FFFFFF;
            margin: 0;
            font-size: 25px;
        }

        .welcome-banner .subtitle {
            color: #E0E7FF;
            margin-top: 7px;
            font-size: 14px;
        }

        .panel-title {
            color: #17365D;
            font-size: 19px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .panel-sub {
            color: #6B7280;
            font-size: 12px;
            margin-bottom: 14px;
        }

        .ann-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-left: 4px solid #17365D;
            padding: 14px 16px;
            border-radius: 10px;
            margin-bottom: 12px;
        }

        .ann-card-title {
            font-weight: 700;
            color: #17365D;
            font-size: 14px;
            overflow-wrap: anywhere;
        }

        .ann-card-body {
            font-size: 12px;
            color: #4B5563;
            margin-top: 6px;
            line-height: 1.6;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }

        .ann-card-meta {
            font-size: 10px;
            color: #6B7280;
            margin-top: 8px;
        }

        .st-key-policy_chat_fab {
            position: fixed !important;
            right: 24px !important;
            bottom: 22px !important;
            z-index: 999999 !important;
            width: fit-content !important;
        }

        .st-key-policy_chat_fab button {
            background: #3730A3 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 30px !important;
            min-height: 52px !important;
            padding: 0 22px !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 15px rgba(32, 38, 94, 0.3);
        }

        .st-key-policy_chat_fab button:hover {
            background: #5148C9 !important;
        }

        .st-key-policy_chat_panel {
            position: fixed !important;
            right: 24px !important;
            bottom: 88px !important;
            width: 420px !important;
            max-width: calc(100vw - 28px) !important;
            max-height: calc(100vh - 120px) !important;
            overflow-y: auto !important;
            background: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 18px !important;
            padding: 18px !important;
            box-shadow: 0 8px 35px rgba(0, 0, 0, 0.20) !important;
            z-index: 999998 !important;
            box-sizing: border-box !important;
        }

        .chat-header {
            color: #17365D;
            font-size: 20px;
            font-weight: 700;
        }

        .chat-subtitle {
            color: #6B7280;
            font-size: 12px;
        }

        .st-key-policy_send_button button {
            background: #3730A3 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 50% !important;
            width: 43px !important;
            height: 43px !important;
            min-height: 43px !important;
            padding: 0 !important;
            font-size: 23px !important;
            font-weight: bold !important;
        }

        .st-key-policy_send_button button:hover {
            background: #5148C9 !important;
        }

        .st-key-policy_close_button button {
            border: none !important;
            background: #F1F3F9 !important;
            color: #3730A3 !important;
            border-radius: 50% !important;
            min-height: 34px !important;
        }

        .employee-portal-footer {
            text-align: center;
            color: #6B7280;
            font-size: 11px;
        }

        #MainMenu,
        footer {
            visibility: hidden;
        }

        @media (max-width: 640px) {
            .st-key-policy_chat_fab {
                right: 12px !important;
                bottom: 12px !important;
            }

            .st-key-policy_chat_panel {
                right: 12px !important;
                bottom: 76px !important;
                width: calc(100vw - 24px) !important;
                max-width: calc(100vw - 24px) !important;
            }
        }
        </style>
    """)


def _fetch_announcements(designation):
    query = urlencode({"designation": designation})
    response = api_request("GET", f"{ANNOUNCEMENTS_ENDPOINT}?{query}")
    response.raise_for_status()

    record = response.json().get("data")
    if isinstance(record, dict) and record.get("announcement_id") is not None:
        return [record]

    return []


def _ask_policy_bot(question, category=None):
    response = api_request(
        "POST",
        POLICY_ASK_ENDPOINT,
        json={"question": question, "category": category},
    )
    response.raise_for_status()

    data = response.json()
    if isinstance(data, dict):
        data = data.get("data", data)

    return data.get("answer"), data.get("sources", [])


def _init_state():
    defaults = {
        "chat_history": [],
        "chat_open": False,
        "announcements": [],
        "ann_loaded": False,
        "ann_loaded_for": None,
        "policy_category_filter": "All Categories",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _render_sidebar():
    with st.sidebar:
        st.html('<h2 class="employee-sidebar-title">Employee Dashboard</h2>')

        profile_picture = st.session_state.get("profile_picture")
        full_name = html.escape(str(st.session_state.get("full_name") or "Employee"))
        designation = html.escape(str(st.session_state.get("designation") or "Employee"))

        if profile_picture:
            with st.container(
                key="employee_profile_photo",
                horizontal=True,
                horizontal_alignment="center",
            ):
                st.image(profile_picture, width=112)

        st.html(
            f"""
            <div class="employee-profile">
                <div class="employee-profile-name">{full_name}</div>
                <div class="employee-profile-designation">{designation}</div>
            </div>
            """
        )

        if st.button(
            "Sign out",
            key="employee_sign_out",
            type="primary",
            width="stretch",
        ):
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()


def _display_sources(sources):
    if not sources:
        return

    with st.expander("View policy sources"):
        for source in sources:
            policy_name = source.get("policy_name", "Company Policy")
            category = source.get("category", "")
            pages = source.get("page_numbers") or source.get("page_number") or []

            if isinstance(pages, int):
                pages = [pages]

            source_text = f"**{policy_name}**"
            if category:
                source_text += f" · {category}"
            if pages:
                source_text += " · Page(s): " + ", ".join(map(str, pages))

            st.markdown(source_text)


def _render_policy_chatbot():
    button_label = "✕ Close" if st.session_state.chat_open else "💬 Ask"

    if st.button(button_label, key="policy_chat_fab", type="primary"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

    if not st.session_state.chat_open:
        return

    with st.container(key="policy_chat_panel", border=True, width=420):
        header_col, close_col = st.columns([5, 1], vertical_alignment="center")

        with header_col:
            st.html("""
                <div class="chat-header">Policy Assistant</div>
                <div class="chat-subtitle">
                    Search company policies and get answers.
                </div>
            """)

        with close_col:
            if st.button("✕", key="policy_close_button", help="Close chatbot"):
                st.session_state.chat_open = False
                st.rerun()

        st.divider()

        category_options = {
            "All Categories": None,
            "Leaves": "Leaves",
            "Refund": "Refund",
            "Privacy": "Privacy",
            "HR": "HR",
            "Other": "Other",
        }

        selected_label = st.selectbox(
            "Search Policy Category",
            options=list(category_options.keys()),
            key="policy_category_filter",
        )
        selected_category = category_options[selected_label]

        if st.button(
            "Clear conversation",
            key="policy_clear_conversation",
            disabled=not st.session_state.chat_history,
        ):
            st.session_state.chat_history = []
            st.rerun()

        with st.container(height=280, border=False):
            if not st.session_state.chat_history:
                st.info("Hello! Select a category and ask me anything about company policies.")
            else:
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        if message.get("sources"):
                            _display_sources(message["sources"])

        with st.form("policy_chat_form", clear_on_submit=True):
            input_col, send_col = st.columns([6, 1], vertical_alignment="center")

            with input_col:
                question = st.text_input(
                    "Your question",
                    placeholder="Ask about company policies...",
                    label_visibility="collapsed",
                )

            with send_col:
                ask_clicked = st.form_submit_button(
                    "↑",
                    key="policy_send_button",
                    help="Send message",
                    width="stretch",
                )

        if ask_clicked:
            question = question.strip()
            if not question:
                st.warning("Please enter a question.")
            else:
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": question,
                })

                with st.spinner("Searching relevant policies..."):
                    answer, sources = _ask_policy_bot(
                        question=question,
                        category=selected_category,
                    )

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })
                st.rerun()


def user_dashboard():
    _init_state()
    _apply_styles()
    _render_sidebar()

    name = html.escape(str(st.session_state.get("full_name") or "Employee"))
    st.html(
        f"""
        <div class="welcome-banner">
            <h2>Welcome back, {name}</h2>
            <div class="subtitle">
                Your workspace for company policies and HR announcements.
            </div>
        </div>
        """
    )

    designation = str(st.session_state.get("designation") or "").strip()
    if designation.lower() in {"hr", "human resources", "admin", "hr manager"}:
        if st.button("Switch to HR dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()

    if (
        not st.session_state.ann_loaded
        or st.session_state.ann_loaded_for != designation
    ):
        if designation:
            with st.spinner("Loading announcements..."):
                st.session_state.announcements = _fetch_announcements(designation)
        else:
            st.session_state.announcements = []

        st.session_state.ann_loaded = True
        st.session_state.ann_loaded_for = designation

    col_main, col_ann = st.columns([2.2, 1.1], gap="large")

    with col_main:
        st.html("""
            <div class="panel-title">Policy Knowledge Base</div>
            <div class="panel-sub">
                Your central place to access company policy information.
            </div>
        """)

        with st.container(border=True):
            st.markdown("### Company Policies")
            st.write(
                "Access information about company policies, employee benefits, "
                "leaves, refunds, privacy and HR procedures."
            )
            st.divider()
            st.markdown("**What can you search?**")
            st.markdown("""
- Leave and attendance policies
- Employee benefits and entitlements
- Refund and reimbursement policies
- Privacy and data protection rules
- HR procedures and company guidelines
            """)
            st.info(
                "Click the Ask button at the bottom-right corner to search "
                "policies using the AI assistant."
            )

    with col_ann:
        st.html("""
            <div class="panel-title"> HR Announcements</div>
            <div class="panel-sub">Latest updates from your HR department.</div>
        """)

        if st.button("Refresh announcements"):
            st.session_state.ann_loaded = False
            st.rerun()

        announcements = st.session_state.announcements or []

        if not announcements:
            st.info("No announcements available for your designation.")

        for announcement in reversed(announcements):
            title = html.escape(str(announcement.get("title") or "Announcement"))
            content = html.escape(str(
                announcement.get("announcement") or announcement.get("content") or ""
            ))
            audience = html.escape(str(announcement.get("designation") or "All Employees"))
            created_at = html.escape(str(announcement.get("created_at") or ""))
            metadata = " · ".join(value for value in (audience, created_at) if value)

            st.html(
                f"""
                <div class="ann-card">
                    <div class="ann-card-title">📌 {title}</div>
                    <div class="ann-card-body">{content}</div>
                    <div class="ann-card-meta">👥 {metadata}</div>
                </div>
                """
            )

    _render_policy_chatbot()

    st.divider()
    st.html('<div class="employee-portal-footer">Nexora | Employee Portal</div>')


if __name__ == "__main__":
    st.set_page_config(
        page_title="Nexora | Employee Portal",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    user_dashboard()