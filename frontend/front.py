
import streamlit as st
import json
import uuid

from websockets.sync.client import connect


# ------------------------------------------------
# 1. PAGE CONFIGURATION
# ------------------------------------------------

st.set_page_config(
    page_title="Job Post Generator",
    page_icon="💼",
    layout="wide"
)

# Shared Nexora backend
BACKEND_WS = "ws://127.0.0.1:8000/ws/chat"


# ------------------------------------------------
# 2. CUSTOM BUTTON STYLING
# ------------------------------------------------

st.markdown("""
<style>

div[data-testid="stFormSubmitButton"] button {
    background-color: #7C3AED !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

div[data-testid="stFormSubmitButton"] button:hover {
    background-color: #6D28D9 !important;
    color: white !important;
}

div[data-testid="stButton"]:has(button[kind="secondary"]) button {
    background-color: #DC2626 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

div[data-testid="stButton"]:has(button[kind="secondary"]) button:hover {
    background-color: #B91C1C !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------
# 3. SESSION STATE
# ------------------------------------------------

defaults = {
    "session_id": str(uuid.uuid4()),
    "job_post": None,
    "application_form": None,
    "job_post_editor": "",
    "application_form_editor": "",
    "job_post_approved": False,
    "application_form_approved": False,
    "drafts_saved": False
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ------------------------------------------------
# 4. WEBSOCKET COMMUNICATION
# ------------------------------------------------

def send_backend_event(event):

    uri = f"{BACKEND_WS}/{st.session_state.session_id}"

    with connect(
        uri,
        open_timeout=20,
        close_timeout=10,
        ping_interval=20,
        ping_timeout=600
    ) as websocket:

        connected = json.loads(websocket.recv())

        if connected.get("type") != "connected":
            raise ConnectionError("WebSocket connection failed.")

        websocket.send(json.dumps(event))

        return json.loads(websocket.recv())


def send_message(message):

    result = send_backend_event({
        "type": "message",
        "message": message
    })

    if result.get("type") == "response":
        return result.get("data", {})

    raise RuntimeError(
        result.get("message", "Unexpected backend response.")
    )


def save_drafts(job_post, application_form):

    return send_backend_event({
        "type": "update_drafts",
        "job_post": job_post,
        "application_form": application_form
    })


def approve_job_post():

    return send_backend_event({
        "type": "approve_job_post"
    })


def approve_application_form():

    return send_backend_event({
        "type": "approve_application_form"
    })


# ------------------------------------------------
# 5. HELPER: SAVE CURRENT EDITS
# ------------------------------------------------

def sync_drafts():

    updated_job_post = json.loads(
        st.session_state.job_post_editor
    )

    updated_application_form = json.loads(
        st.session_state.application_form_editor
    )

    result = save_drafts(
        updated_job_post,
        updated_application_form
    )

    if result.get("type") != "drafts_updated":

        raise RuntimeError(
            result.get("message", "Could not save drafts.")
        )

    st.session_state.job_post = updated_job_post
    st.session_state.application_form = updated_application_form

    st.session_state.drafts_saved = True


# ------------------------------------------------
# 6. HEADER
# ------------------------------------------------

st.title("💼📑 Job Post Generator")

st.write(
    "Enter job requirements and let AI generate "
    "a professional job post and candidate application form."
)

st.divider()


# ------------------------------------------------
# 7. INITIAL PROMPT
# ------------------------------------------------

if not st.session_state.job_post:

    st.subheader("Enter Job Requirements")

    with st.form("job_requirements_form"):

        user_prompt = st.text_area(
            "Describe the job requirements",
            placeholder=(
                "Example: We are hiring a Python Developer "
                "with 2 years of experience..."
            ),
            height=220
        )

        generate_button = st.form_submit_button(
            "Generate Job Post and Application Form",
            use_container_width=True,
            type="primary"
        )

    if generate_button:

        if not user_prompt.strip():

            st.warning("Please enter job requirements.")

        else:

            with st.spinner(
                "AI is generating your job post and application questions..."
            ):

                try:

                    result = send_message(user_prompt)

                    if result.get("type") != "draft":

                        raise RuntimeError(
                            result.get(
                                "message",
                                "AI could not generate the drafts."
                            )
                        )

                    st.session_state.job_post = result["job_post"]

                    st.session_state.application_form = (
                        result["application_form"]
                    )

                    st.session_state.job_post_editor = json.dumps(
                        result["job_post"],
                        indent=4
                    )

                    st.session_state.application_form_editor = json.dumps(
                        result["application_form"],
                        indent=4
                    )

                    st.session_state.job_post_approved = False
                    st.session_state.application_form_approved = False
                    st.session_state.drafts_saved = True

                    st.success("Both drafts generated successfully!")

                    st.rerun()

                except Exception as error:

                    st.error("Could not generate the drafts.")

                    st.exception(error)


# ------------------------------------------------
# 8. GENERATED DRAFTS
# ------------------------------------------------

if st.session_state.job_post and st.session_state.application_form:

    job_post = st.session_state.job_post
    application_form = st.session_state.application_form

    st.success("Both AI-generated drafts are ready for review.")

    job_column, form_column = st.columns(2, gap="large")

    # JOB POST

    with job_column:

        st.subheader("1. Job Description")

        st.text_area(
            "Edit Job Post JSON",
            key="job_post_editor",
            height=550
        )

        st.markdown("**Job Post Preview**")

        st.markdown(
            f"### {job_post.get('job_title') or 'Job Title'}"
        )

        st.write(job_post.get("role_summary", ""))

        st.markdown("**Responsibilities**")

        for item in job_post.get("responsibilities", []):
            st.markdown(f"- {item}")

        st.markdown("**Required Skills**")

        for skill in job_post.get("required_skills", []):
            st.markdown(f"- {skill}")

        if st.session_state.job_post_approved:
            st.success("Job post approved.")
        else:
            st.info("Job post approval pending.")

    # APPLICATION FORM

    with form_column:

        st.subheader("2. Candidate Application Form")

        st.text_area(
            "Edit Application Form JSON",
            key="application_form_editor",
            height=550
        )

        st.markdown("**Application Questions Preview**")

        st.markdown(
            f"**{application_form.get('form_title', 'Application Form')}**"
        )

        for index, question in enumerate(
            application_form.get("questions", []),
            start=1
        ):

            st.markdown(
                f"**{index}. {question.get('question', '')}**"
            )

            st.caption(
                f"Type: {question.get('type', '')} | "
                f"Required: {question.get('required', False)}"
            )

            for option in question.get("options", []):
                st.write(f"- {option}")

        if st.session_state.application_form_approved:
            st.success("Application questions approved.")
        else:
            st.info("Application questions approval pending.")

    # SAVE BOTH DRAFTS

    st.divider()

    if st.button(
        "Save Both Drafts",
        use_container_width=True
    ):

        try:

            sync_drafts()

            st.session_state.job_post_approved = False
            st.session_state.application_form_approved = False

            st.success("Both edited drafts saved successfully.")

            st.rerun()

        except (json.JSONDecodeError, RuntimeError) as error:

            st.error(f"Could not save drafts: {error}")

    # APPROVAL BUTTONS

    approval_column1, approval_column2 = st.columns(2)

    with approval_column1:

        if st.button(
            "Approve Job Post",
            disabled=st.session_state.job_post_approved,
            use_container_width=True
        ):

            try:

                sync_drafts()

                result = approve_job_post()

                if result.get("type") == "approval":

                    st.session_state.job_post_approved = True

                    st.success("Job post approved!")

                    st.rerun()

                raise RuntimeError(
                    result.get("message", "Approval failed.")
                )

            except Exception as error:

                st.error(f"Approval failed: {error}")

    with approval_column2:

        if st.button(
            "Approve Application Questions",
            disabled=st.session_state.application_form_approved,
            use_container_width=True
        ):

            try:

                sync_drafts()

                result = approve_application_form()

                if result.get("type") == "approval":

                    st.session_state.application_form_approved = True

                    st.success("Application questions approved!")

                    st.rerun()

                raise RuntimeError(
                    result.get("message", "Approval failed.")
                )

            except Exception as error:

                st.error(f"Approval failed: {error}")

    # FINAL APPROVAL STATUS

    st.divider()

    st.subheader("3. Final Approval Status")

    st.write(
        "Job Post:",
        "Approved" if st.session_state.job_post_approved
        else "Pending"
    )

    st.write(
        "Application Questions:",
        "Approved" if st.session_state.application_form_approved
        else "Pending"
    )

    if (
        st.session_state.job_post_approved
        and st.session_state.application_form_approved
    ):

        st.success(
            "Both drafts are approved and ready for handoff."
        )

        approved_payload = {
            "job_post": st.session_state.job_post,
            "application_form": st.session_state.application_form,
            "approved": True
        }

        st.download_button(
            "Download Approved JSON",
            data=json.dumps(approved_payload, indent=4),
            file_name="approved_job_application.json",
            mime="application/json",
            use_container_width=True
        )

        st.info(
            "Your teammate can use this JSON payload "
            "for the Google Forms integration."
        )


# ------------------------------------------------
# 9. START NEW JOB POST
# ------------------------------------------------

st.divider()

if st.button(
    "Start New Job Post",
    type="secondary",
    use_container_width=True,
    key="start_new_job"
):

    st.session_state.session_id = str(uuid.uuid4())

    st.session_state.job_post = None
    st.session_state.application_form = None

    st.session_state.job_post_editor = ""
    st.session_state.application_form_editor = ""

    st.session_state.job_post_approved = False
    st.session_state.application_form_approved = False
    st.session_state.drafts_saved = False

    st.rerun()
