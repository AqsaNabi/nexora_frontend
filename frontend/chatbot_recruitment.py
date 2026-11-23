import os
import sys

import streamlit as st

def chatbot_recruitment_function():
    # The frontend file is in the project root, so use this directory
    # as the import root for the existing repository package.
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)


    from job_post_functions import (
        initialize_session_state,
        send_message,
        process_pending_message,
        approve_both_drafts,
        start_new_job_post
    )


    # ============================================================
    # STYLING  (ORANGE & WHITE THEME)
    # ============================================================

    def apply_styling():
        st.markdown(
            """
            <style>
            /* ---------- GLOBAL / PAGE ---------- */
            .stApp {
                background-color: #FFF8F2;          /* warm off-white */
                color: #3A2A1E;                      /* dark warm brown text */
            }

            .block-container {
                max-width: 1250px;
                padding-top: 1.5rem;
                padding-bottom: 3rem;
            }

            h1, h2, h3, h4 {
                color: #C2410C !important;           /* deep orange headings */
                font-weight: 750 !important;
            }

            .stMarkdown p,
            .stMarkdown li,
            .stMarkdown span,
            .stMarkdown label {
                color: #3A2A1E !important;
            }

            /* ---------- CHAT MESSAGES ---------- */
            [data-testid="stChatMessage"] {
                background-color: #FFFFFF;
                border: 1px solid #FED7AA;           /* soft orange border */
                border-radius: 14px;
                padding: 16px;
                box-shadow: 0 1px 3px rgba(194, 65, 12, 0.06);
            }

            /* make user vs assistant bubbles slightly distinct */
            [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
                background-color: #FFF3E6;           /* pale orange for user */
                border-color: #FDBA74;
            }

            /* ---------- TEXT INPUTS / TEXTAREAS ---------- */
            .stTextInput input,
            .stTextArea textarea {
                background-color: #FFFFFF !important;
                color: #3A2A1E !important;
                border: 1px solid #FED7AA !important;
                border-radius: 10px !important;
            }

            .stTextInput input::placeholder,
            .stTextArea textarea::placeholder {
                color: #9A7B66 !important;
            }

            /* ---------- BUTTONS ---------- */
            div.stButton > button {
                min-height: 44px;
                border-radius: 10px;
                font-weight: 600;
                border: 1px solid #FED7AA;
                color: #C2410C;
                background-color: #FFFFFF;
            }

            div.stButton > button:hover {
                background-color: #FFF3E6;
                border-color: #FDBA74;
            }

            div.stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #F97316, #EA580C) !important;
                border: 1px solid #EA580C !important;
                color: white !important;
            }

            div.stButton > button[kind="primary"]:hover {
                background: linear-gradient(135deg, #EA580C, #C2410C) !important;
            }

            /* ---------- SIDEBAR ---------- */
            [data-testid="stSidebar"] {
                background: linear-gradient(
                    180deg,
                    #FFF3E6 0%,
                    #FFE8D1 55%,
                    #FED7AA 100%
                ) !important;
                border-right: 1px solid #FDBA74 !important;
            }

            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] span,
            [data-testid="stSidebar"] .stMarkdown {
                color: #7C2D12 !important;           /* dark burnt-orange text */
            }

            [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
                color: #9A5B3A !important;
            }

            [data-testid="stSidebar"] hr {
                border-color: rgba(194, 65, 12, 0.25) !important;
            }

            [data-testid="stSidebar"] div.stButton > button {
                width: 100%;
                background: linear-gradient(135deg, #F97316, #EA580C) !important;
                color: white !important;
                border: 1px solid rgba(255,255,255,0.35) !important;
                border-radius: 11px !important;
            }

            [data-testid="stSidebar"] div.stButton > button:hover {
                background: linear-gradient(135deg, #EA580C, #C2410C) !important;
            }

            /* ---------- EXPANDERS / CODE / DIVIDERS ---------- */
            [data-testid="stExpander"] {
                background-color: #FFFFFF;
                border: 1px solid #FED7AA;
                border-radius: 12px;
            }

            [data-testid="stCode"] {
                background-color: #FFF3E6 !important;
                border-radius: 10px;
            }

            /* ---------- CHAT INPUT (bottom bar) ---------- */
            div[data-testid="stChatInput"] textarea {
                color: #3A2A1E !important;
                -webkit-text-fill-color: #3A2A1E !important;
                caret-color: #C2410C !important;
            }

            div[data-testid="stChatInput"] textarea::placeholder {
                color: #9A7B66 !important;
                -webkit-text-fill-color: #9A7B66 !important;
            }

            /* chat input container border */
            div[data-testid="stChatInput"] {
                border: 1px solid #FDBA74 !important;
                border-radius: 12px !important;
                background-color: #FFFFFF !important;
            }

            hr {
                border-color: #FED7AA !important;
            }

            .stCaption {
                color: #9A7B66 !important;
            }

            /* ---------- ALERTS ---------- */
            [data-testid="stAlert"] {
                border-radius: 10px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )


    # ============================================================
    # SIDEBAR
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


    # ============================================================
    # CHAT DISPLAY
    # ============================================================

    def display_chat_messages():
        for message in st.session_state.chat_messages:
            role = message.get("role", "assistant")
            content = message.get("content", "")

            if role not in ["user", "assistant"] or not content:
                continue

            with st.chat_message(role):
                st.markdown(content)


    # ============================================================
    # WELCOME SECTION
    # ============================================================

    def display_welcome_section():
        if st.session_state.chat_messages:
            return

        _, center_content, _ = st.columns([1, 5, 1])

        with center_content:
            st.markdown(
                """
                <h3 style='text-align:center; color:#F97316;'>
                    Let's Get Started!
                </h3>
                <h2 style='text-align:center; color:#C2410C;'>
                    Your hiring journey starts here.
                </h2>
                <p style="
                    text-align:center;
                    color:#9A7B66;
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
    # JOB POST PREVIEW
    # ============================================================

    def display_job_post():
        job_post = st.session_state.current_job_post

        if not job_post:
            return

        st.subheader("Job Description")

        if job_post.get("job_title"):
            st.markdown(f"### {job_post['job_title']}")

        fields = [
            ("Department", "department"),
            ("Location", "location"),
            ("Work Mode", "work_mode"),
            ("Employment Type", "employment_type"),
            ("Experience", "experience"),
            ("Salary Range", "salary_range"),
            ("Role Summary", "role_summary"),
            ("Job Description", "job_description"),
            ("Responsibilities", "responsibilities"),
            ("Required Skills", "required_skills"),
            ("Preferred Skills", "preferred_skills"),
            ("Education", "education"),
            ("Benefits", "benefits"),
            ("Application Instructions", "application_instructions")
        ]

        for label, key in fields:
            value = job_post.get(key)

            if not value:
                continue

            st.markdown(f"**{label}**")

            if isinstance(value, list):
                for item in value:
                    st.markdown(f"- {item}")
            else:
                st.write(value)


    # ============================================================
    # APPLICATION FORM PREVIEW
    # ============================================================

    def display_application_form():
        application_form = st.session_state.current_application_form

        if not application_form:
            return

        st.subheader("Application Form")

        form_title = application_form.get("form_title")

        if form_title:
            st.markdown(f"### {form_title}")

        questions = application_form.get("questions", [])

        if not isinstance(questions, list):
            st.warning("The generated application questions are invalid.")
            return

        for index, question in enumerate(questions, start=1):
            if not isinstance(question, dict):
                continue

            with st.container(border=True):
                question_text = question.get(
                    "question",
                    question.get("field_name", "")
                )

                st.markdown(f"**{index}. {question_text}**")

                field_type = question.get("type", "text")
                st.caption(
                    f"Answer type: {field_type.replace('_', ' ').title()}"
                )

                if question.get("required"):
                    st.caption("Required")

                options = question.get("options", [])

                if options:
                    st.caption("Options: " + ", ".join(map(str, options)))


    # ============================================================
    # REVIEW AND APPROVAL
    # ============================================================

    def display_review_section():
        job_post = st.session_state.current_job_post
        application_form = st.session_state.current_application_form

        if not job_post or not application_form:
            return

        st.divider()
        st.header("Review Your Recruitment Content")

        with st.expander("Job Description", expanded=True):
            display_job_post()

        with st.expander("Application Form", expanded=True):
            display_application_form()

        st.divider()

        if st.session_state.is_approved:
            st.success(
                "The job post and application form have been approved successfully."
            )

            if st.session_state.recruitment_post_id:
                st.write(
                    "Recruitment Post ID: "
                    f"{st.session_state.recruitment_post_id}"
                )

            if st.session_state.google_form_url:
                st.subheader("Candidate Application Link")
                st.markdown(
                    f"[Open Google Application Form]"
                    f"({st.session_state.google_form_url})"
                )
                st.code(st.session_state.google_form_url, language=None)
            else:
                st.warning(
                    "Approval was confirmed, but the backend did not return a Google Form URL."
                )

            return

        st.subheader("Final Approval")
        st.write(
            "Review both sections above. Once everything is correct, "
            "approve them to create the recruitment post and candidate application form."
        )

        if st.button(
            "Approve Job Post & Application Form",
            type="primary",
            use_container_width=True
        ):
            approve_both_drafts()


    # ============================================================
    # MAIN CHATBOT PAGE
    # ============================================================

    def job_post_generator():
        initialize_session_state()
        apply_styling()
        display_sidebar()

        st.title("Job Post Generator")
        st.caption("AI-powered job post and application form generator")
        st.divider()

        process_pending_message()

        display_welcome_section()
        display_chat_messages()
        display_review_section()

        if not st.session_state.is_approved:
            user_message = st.chat_input(
                "Describe the job position you want to create..."
            )

            if user_message:
                send_message(user_message)

        elif st.session_state.google_form_url:
            st.markdown("### Google Application Form")
            st.link_button(
                "Open Google Form",
                st.session_state.google_form_url
            )


    # if __name__ == "__main__":
    job_post_generator()
# chatbot_recruitment_function()