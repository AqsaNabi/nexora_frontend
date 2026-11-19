
import streamlit as st
import requests

from api import api_request, API_URL

UPDATE_POLICY_ENDPOINT = "/policies/upload"


# ==========================================
# HR SIDEBAR
# ==========================================

def hr_sidebar():

    st.sidebar.title("HR Portal")

    if st.sidebar.button(
        "← Back to Main Dashboard", type="primary",
        use_container_width=True
    ):
        st.session_state.page = "dashboard"
        st.rerun()

    st.sidebar.divider()

    # HR Profile Picture
    profile_pic = st.session_state.get("profile_picture")

    if profile_pic:
        try:
            st.sidebar.image(profile_pic, width=110)
        except Exception:
            pass

    # HR Full Name
    full_name = st.session_state.get(
        "full_name",
        "HR Administrator"
    )

    st.sidebar.write(f"**{full_name}**")
    st.sidebar.caption("Human Resources Department")

    st.sidebar.divider()


# ==========================================
# PAGE STYLING
# ==========================================

def apply_styles():

    st.markdown("""
    <style>

    .stApp {
        background-color: #f5f6fc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    h1, h2, h3 {
        color: #20265E !important;
    }

    .policy-header {
        background: linear-gradient(
            120deg,
            #20265E 0%,
            #3730A3 55%,
            #5148C9 100%
        );
        padding: 30px 34px;
        border-radius: 16px;
        margin-bottom: 22px;
        box-shadow: 0 4px 16px rgba(32, 38, 94, 0.12);
    }

    .policy-header h1 {
        color: #ffffff !important;
        font-size: 28px;
        font-weight: 700;
        margin: 0 0 10px 0;
        padding: 0;
    }

    .policy-header .subtitle {
        color: #e0e4ff;
        font-size: 14px;
        line-height: 1.6;
        margin: 0;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 9px;
        font-weight: 600;
        min-height: 44px;
    }

    label {
        color: #20265E !important;
        font-weight: 600 !important;
    }

    </style>
    """, unsafe_allow_html=True)


# ==========================================
# POLICY UPLOAD API
# ==========================================

def update_policy(description, category, uploaded_file):

    response = api_request(
        method="POST",
        endpoint=UPDATE_POLICY_ENDPOINT,

        # Form fields sent to FastAPI
        data={
            "description": description,
            "category": category
        },

        # Uploaded PDF file
        files={
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf"
            )
        }
    )

    return response


# ==========================================
# POLICY MANAGEMENT PAGE
# ==========================================

def policies():

    hr_sidebar()
    apply_styles()

    # HEADER

    st.markdown(
        '<div class="policy-header"><h1>Policy Knowledge Management</h1><div class="subtitle">Upload and manage company policies. The AI Policy Assistant processes these documents to answer employee queries.</div></div>',
        unsafe_allow_html=True
    )

    # POLICY UPLOAD FORM

    with st.container(border=True):

        st.subheader("Upload Company Policy")

        st.caption(
            "Select a policy category, provide its description "
            "and upload the PDF document."
        )

        with st.form(
            key="policy_update_form",
            clear_on_submit=False
        ):

            # FIELD 1: POLICY CATEGORY

            categories = [
                "Refund",
                "Privacy",
                "HR",
                "Other"
            ]

            category = st.selectbox(
                "Policy Category *",
                options=categories
            )

            # FIELD 2: DESCRIPTION

            description = st.text_area(
                "Policy Description *",
                placeholder="Describe what this policy covers...",
                height=120
            )

            # FIELD 3: PDF DOCUMENT

            uploaded_file = st.file_uploader(
                "Upload Policy Document *",
                type=["pdf"],
                help="Only PDF documents are accepted."
            )

            st.write("")

            update_clicked = st.form_submit_button(
                "Upload & Index Policy",
                type="primary",
                use_container_width=True
            )

        # ======================================
        # FORM SUBMISSION
        # ======================================

        if update_clicked:

            if not description.strip():

                st.warning(
                    "Please enter a policy description."
                )

            elif uploaded_file is None:

                st.warning(
                    "Please upload a PDF policy document."
                )

            else:

                try:

                    with st.spinner(
                        "Uploading and indexing policy... Please wait."
                    ):

                        response = update_policy(
                            description=description.strip(),
                            category=category,
                            uploaded_file=uploaded_file
                        )

                    if response.status_code in [200, 201]:

                        try:
                            result = response.json()

                            msg = result.get(
                                "message",
                                "Policy uploaded successfully!"
                            )

                        except Exception:
                            msg = "Policy uploaded successfully!"

                        st.success(f"✅ {msg}")
                        st.toast(msg, icon="✅")

                    else:

                        detail = "Unable to upload the policy."

                        try:
                            detail = response.json().get(
                                "detail",
                                detail
                            )
                        except Exception:
                            pass

                        st.error(
                            f"Upload failed: {detail} "
                            f"(Status {response.status_code})"
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        f"Cannot connect to backend at {API_URL}. "
                        "Please ensure the server is running."
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "Request timed out while processing "
                        "the policy document."
                    )

                except requests.exceptions.RequestException:

                    st.error(
                        "A network error occurred. Please try again."
                    )

    st.divider()

    st.caption("Nexora HR Portal | Policy Knowledge Base")


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    st.set_page_config(
        page_title="Nexora | Policy Management",
        page_icon="📚",
        layout="wide"
    )

    policies()
