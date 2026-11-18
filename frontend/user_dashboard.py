
import base64
import html
from urllib.parse import urlencode

import streamlit as st

from api import api_request


# =====================================================
# API ENDPOINTS
# =====================================================

ANNOUNCEMENTS_ENDPOINT = "/announcements/latest"
POLICY_ASK_ENDPOINT = "/user/policies/ask"


# =====================================================
# STYLING
# =====================================================

def _apply_styles():

    st.markdown("""
    <style>

    .stApp {
        background: #F4F7FB;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        background: #17365d !important;
        border-right: none !important;
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.12) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        color: white !important;
        border-radius: 10px;
        font-weight: 600;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,75,75,0.85) !important;
        border-color: #FF4B4B !important;
    }

    /* Welcome banner */

    .welcome-banner {
        background: linear-gradient(
            120deg,
            #17365d,
            #3730A3,
            #5148C9
        );
        padding: 24px 28px;
        border-radius: 14px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 4px 16px rgba(32,38,94,0.12);
    }

    .welcome-banner h2 {
        color: white !important;
        margin: 0;
        font-size: 25px;
    }

    .welcome-banner .subtitle {
        color: #E0E7FF;
        margin-top: 7px;
        font-size: 14px;
    }

    /* Dashboard headings */

    .panel-title {
        color: #17365d;
        font-size: 19px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .panel-sub {
        color: #6B7280;
        font-size: 12px;
        margin-bottom: 14px;
    }

    /* Announcement cards */

    .ann-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-left: 4px solid #17365d;
        padding: 14px 16px;
        border-radius: 10px;
        margin-bottom: 12px;
    }

    .ann-card-title {
        font-weight: 700;
        color: #17365d;
        font-size: 14px;
    }

    .ann-card-body {
        font-size: 12px;
        color: #4B5563;
        margin-top: 6px;
        line-height: 1.6;
        white-space: pre-wrap;
    }

    .ann-card-meta {
        font-size: 10px;
        color: #9CA3AF;
        margin-top: 8px;
    }

    /* Floating Ask button */

    .st-key-policy_chat_fab {
        position: fixed !important;
        right: 24px !important;
        bottom: 22px !important;
        z-index: 999999 !important;
        width: fit-content !important;
    }

    .st-key-policy_chat_fab button {
        background: #3730A3 !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        min-height: 52px !important;
        padding: 0 22px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(32,38,94,0.3);
    }

    .st-key-policy_chat_fab button:hover {
        background: #5148C9 !important;
        color: white !important;
    }

    /* Floating chatbot panel */

    .st-key-policy_chat_panel {
        position: fixed !important;
        right: 24px !important;
        bottom: 88px !important;
        width: 420px !important;
        max-width: calc(100vw - 28px) !important;
        max-height: calc(100vh - 120px) !important;
        overflow-y: auto !important;
        background: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 18px !important;
        padding: 18px !important;
        box-shadow: 0 8px 35px rgba(0,0,0,0.20) !important;
        z-index: 999998 !important;
        box-sizing: border-box !important;
    }

    .chat-header {
        color: #17365d;
        font-size: 20px;
        font-weight: 700;
    }

    .chat-subtitle {
        color: #6B7280;
        font-size: 12px;
    }

    /* Send arrow */

    .st-key-policy_send_button button {
        background: #3730A3 !important;
        color: white !important;
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

    /* Close button */

    .st-key-policy_close_button button {
        border: none !important;
        background: #F1F3F9 !important;
        color: #3730A3 !important;
        border-radius: 50% !important;
        min-height: 34px !important;
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
    """, unsafe_allow_html=True)


# =====================================================
# FETCH ANNOUNCEMENTS BY DESIGNATION
# JWT HANDLED BY api_request()
# =====================================================
def _fetch_announcements(designation):
    audience_by_designation = {
        "manager": "Managers",
        "managers": "Managers",
        "team leader": "Team Leaders",
        "team leaders": "Team Leaders",
        "tl": "Team Leaders",
        "tls": "Team Leaders",
    }

    audience = audience_by_designation.get((designation or "").strip().lower())
    if audience is None:
        return []

    query = urlencode({"designation": audience})
    response = api_request("GET", f"{ANNOUNCEMENTS_ENDPOINT}?{query}")
    response.raise_for_status()

    record = response.json().get("data")
    if isinstance(record, dict) and record.get("announcement_id") is not None:
        return [record]

    return []


# =====================================================
# ASK POLICY QUESTION
# JWT HANDLED BY api_request()
# =====================================================

def _ask_policy_bot(question, category=None):

    response = api_request(
        "POST",
        POLICY_ASK_ENDPOINT,
        json={
            "question": question,
            "category": category
        }
    )

    response.raise_for_status()

    data = response.json()

    if isinstance(data, dict):
        data = data.get("data", data)

    answer = data.get("answer")
    sources = data.get("sources", [])

    return answer, sources


# =====================================================
# SESSION STATE
# =====================================================

def _init_state():

    defaults = {
        "chat_history": [],
        "chat_open": False,
        "announcements": [],
        "ann_loaded": False,
        "ann_loaded_for": None,
        "policy_category_filter": "All Categories"
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# =====================================================
# AVATAR PLACEHOLDER
# =====================================================

def _avatar_placeholder(name):

    initial = (
        html.escape(str(name)[0].upper())
        if name else "?"
    )

    st.markdown(
        f"""
        <div style="display:flex;justify-content:center;
                    margin-bottom:4px;">
            <div style="width:80px;height:80px;
                        border-radius:50%;
                        background:linear-gradient(135deg,#818CF8,#3730A3);
                        color:white;
                        display:flex;align-items:center;
                        justify-content:center;
                        font-size:34px;font-weight:700;">
                {initial}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# SIDEBAR
# PROFILE DETAILS FROM SESSION STATE
# SAME APPROACH AS HR DASHBOARD
# =====================================================

def _render_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div style="text-align:center;padding:16px 0 10px 0;">
                <span style="font-size:28px;">🏢</span>

                <h2 style="margin:6px 0 2px 0;font-size:20px;">
                    NEXORA
                </h2>

                <p style="font-size:11px;color:#C7C9E9;margin:0;">
                    Employee Portal
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        # Read details populated during login

        profile_pic = st.session_state.get("profile_picture")

        full_name = st.session_state.get(
            "full_name",
            "Employee"
        )

        designation = st.session_state.get(
            "designation",
            ""
        )

        # Profile picture - same as HR dashboard

        if profile_pic:

            st.image(
                profile_pic,
                width=100
            )

        else:

            _avatar_placeholder(full_name)

        # Employee information

        st.markdown(
            f"""
            <div style="text-align:center;padding:8px 0 4px 0;">

                <div style="font-size:17px;font-weight:700;">
                    {html.escape(str(full_name))}
                </div>

                <div style="font-size:12px;color:#C7C9E9;margin-top:3px;">
                    {html.escape(str(designation))}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        # Switch to HR Dashboard

        user_role = str(designation).strip().lower()

        if user_role in [
            "hr",
            "human resources",
            "admin",
            "hr manager"
        ]:

            if st.button(
                "🏢 Switch to HR Dashboard",
                use_container_width=True
            ):

                st.session_state.page = "dashboard"
                st.rerun()

        # Refresh announcements

        if st.button(
            "↻ Refresh Announcements",
            use_container_width=True
        ):

            st.session_state.ann_loaded = False
            st.session_state.ann_loaded_for = None
            st.rerun()

        # Clear chatbot history

        if st.button(
            "🗑 Clear Chat",
            use_container_width=True
        ):

            st.session_state.chat_history = []
            st.rerun()

        st.divider()

        # Sign out

        if st.button(
            "⬅ Sign Out",
            use_container_width=True
        ):

            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.session_state.page = "login"
            st.rerun()

        st.markdown(
            """
            <div style="text-align:center;font-size:10px;
                        color:#C7C9E9;padding-top:20px;">
                © 2026 Nexora
            </div>
            """,
            unsafe_allow_html=True
        )


# =====================================================
# DISPLAY POLICY SOURCES
# =====================================================

def _display_sources(sources):

    if not sources:
        return

    with st.expander("📚 View policy sources"):

        for source in sources:

            policy_name = source.get(
                "policy_name",
                "Company Policy"
            )

            category = source.get("category", "")

            pages = (
                source.get("page_numbers")
                or source.get("page_number")
                or []
            )

            if isinstance(pages, int):
                pages = [pages]

            source_text = f"**{policy_name}**"

            if category:
                source_text += f" · {category}"

            if pages:

                source_text += (
                    " · Page(s): "
                    + ", ".join(map(str, pages))
                )

            st.markdown(source_text)


# =====================================================
# FLOATING POLICY CHATBOT
# =====================================================

def _render_policy_chatbot():

    button_label = (
        "✕ Close"
        if st.session_state.chat_open
        else "💬 Ask"
    )

    if st.button(
        button_label,
        key="policy_chat_fab",
        type="primary"
    ):

        st.session_state.chat_open = (
            not st.session_state.chat_open
        )

        st.rerun()

    if not st.session_state.chat_open:
        return

    with st.container(
        key="policy_chat_panel",
        border=True,
        width=420
    ):

        header_col, close_col = st.columns(
            [5, 1],
            vertical_alignment="center"
        )

        with header_col:

            st.markdown(
                """
                <div class="chat-header">
                    Policy Assistant
                </div>

                <div class="chat-subtitle">
                    Search company policies and get answers.
                </div>
                """,
                unsafe_allow_html=True
            )

        with close_col:

            if st.button(
                "✕",
                key="policy_close_button",
                help="Close chatbot"
            ):

                st.session_state.chat_open = False
                st.rerun()

        st.divider()

        # Category dropdown

        category_options = {
            "All Categories": None,
            "Leaves": "Leaves",
            "Refund": "Refund",
            "Privacy": "Privacy",
            "HR": "HR",
            "Other": "Other"
        }

        selected_label = st.selectbox(
            "Search Policy Category",
            options=list(category_options.keys()),
            key="policy_category_filter"
        )

        selected_category = category_options[selected_label]

        # Chat history

        chat_container = st.container(
            height=280,
            border=False
        )

        with chat_container:

            if not st.session_state.chat_history:

                st.info(
                    "Hello! Select a category and ask me "
                    "anything about company policies."
                )

            else:

                for msg in st.session_state.chat_history:

                    with st.chat_message(msg["role"]):

                        st.markdown(msg["content"])

                        if msg.get("sources"):
                            _display_sources(msg["sources"])

        # Question input and arrow

        with st.form(
            "policy_chat_form",
            clear_on_submit=True
        ):

            input_col, send_col = st.columns(
                [6, 1],
                vertical_alignment="center"
            )

            with input_col:

                question = st.text_input(
                    "Your question",
                    placeholder="Ask about company policies...",
                    label_visibility="collapsed"
                )

            with send_col:

                ask_clicked = st.form_submit_button(
                    "↑",
                    key="policy_send_button",
                    help="Send message",
                    use_container_width=True
                )

        # Process question

        if ask_clicked:

            if not question.strip():

                st.warning("Please enter a question.")

            else:

                st.session_state.chat_history.append({
                    "role": "user",
                    "content": question.strip()
                })

                with st.spinner("Searching relevant policies..."):

                    answer, sources = _ask_policy_bot(
                        question=question.strip(),
                        category=selected_category
                    )

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

                st.rerun()


# =====================================================
# MAIN USER DASHBOARD
# =====================================================

def user_dashboard():

    _init_state()

    _apply_styles()

    _render_sidebar()

    # Welcome banner

    full_name = st.session_state.get(
        "full_name",
        "Employee"
    )

    name = html.escape(str(full_name))

    st.markdown(
        f"""
        <div class="welcome-banner">
            <h2>Welcome back, {name}</h2>

            <div class="subtitle">
                Your workspace for company policies
                and HR announcements.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==========================================
    # FETCH ANNOUNCEMENTS BY DESIGNATION
    # ==========================================

    designation = str(
        st.session_state.get("designation", "")
    ).strip()

    if (
        not st.session_state.ann_loaded
        or st.session_state.ann_loaded_for != designation
    ):

        if designation:

            with st.spinner("Loading announcements..."):

                announcements = _fetch_announcements(designation)

            st.session_state.announcements = announcements
            st.session_state.ann_loaded = True
            st.session_state.ann_loaded_for = designation

        else:

            st.session_state.announcements = []
            st.session_state.ann_loaded = True
            st.session_state.ann_loaded_for = designation

    # ==========================================
    # TWO-COLUMN DASHBOARD
    # ==========================================

    col_main, col_ann = st.columns(
        [2.2, 1.1],
        gap="large"
    )

    # LEFT: POLICY KNOWLEDGE BASE

    with col_main:

        st.markdown(
            """
            <div class="panel-title">
                Policy Knowledge Base
            </div>

            <div class="panel-sub">
                Your central place to access company policy information.
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container(border=True):

            st.markdown("### 📚 Company Policies")

            st.write(
                "Access information about company policies, "
                "employee benefits, leaves, refunds, privacy "
                "and HR procedures."
            )

            st.divider()

            st.markdown("**What can you search?**")

            st.markdown(
                """
                - Leave and attendance policies
                - Employee benefits and entitlements
                - Refund and reimbursement policies
                - Privacy and data protection rules
                - HR procedures and company guidelines
                """
            )

            st.info(
                "Click the Ask button at the bottom-right "
                "corner to search policies using the AI assistant."
            )

    # RIGHT: HR ANNOUNCEMENTS

    with col_ann:

        st.markdown(
            """
            <div class="panel-title">
                📢 HR Announcements
            </div>

            <div class="panel-sub">
                Latest updates from your HR department.
            </div>
            """,
            unsafe_allow_html=True
        )

        announcements = st.session_state.announcements or []

        if not announcements:

            st.info(
                "No announcements available for your designation."
            )

        else:

            for ann in reversed(announcements):

                title = html.escape(
                    str(ann.get("title") or "Announcement")
                )

                content = html.escape(
                    str(
                        ann.get("announcement")
                        or ann.get("content")
                        or ""
                    )
                )

                created_at = html.escape(
                    str(ann.get("created_at") or "")
                )

                audience = html.escape(
                    str(
                        ann.get("designation")
                        or "All Employees"
                    )
                )

                st.markdown(
                    f"""
                    <div class="ann-card">

                        <div class="ann-card-title">
                            📌 {title}
                        </div>

                        <div class="ann-card-body">
                            {content}
                        </div>

                        <div class="ann-card-meta">
                            👥 {audience}
                            {"&nbsp;·&nbsp;" + created_at if created_at else ""}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Floating chatbot

    _render_policy_chatbot()

    # Footer

    st.divider()

    st.markdown(
        """
        <div style="text-align:center;color:#9CA3AF;
                    font-size:11px;">
            Nexora | Employee Portal
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    st.set_page_config(
        page_title="Nexora | Employee Portal",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    user_dashboard()
