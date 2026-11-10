
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

BACKEND_WS = "ws://127.0.0.1:8000/ws/chat"


# ------------------------------------------------
# 2. SESSION STATE
# ------------------------------------------------

defaults = {
    "session_id": str(uuid.uuid4()),
    "job_post": None,
    "application_form": None,
    "job_post_editor": "",
    "application_form_editor": "",
    "job_post_approved": False,
    "application_form_approved": False,
    "drafts_saved": False,
    "approved_payload": None,
    "saved_file": None
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ------------------------------------------------
# 3. WEBSOCKET COMMUNICATION
# ------------------------------------------------

def send_backend_event(event):

    uri = (
        f"{BACKEND_WS}/"
        f"{st.session_state.session_id}"
    )

    with connect(
        uri,
        open_timeout=20,
        close_timeout=10,
        ping_interval=20,
        ping_timeout=600
    ) as websocket:

        connected = json.loads(websocket.recv())

        if connected.get("type") != "connected":
            raise ConnectionError(
                "WebSocket connection failed."
            )

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
        result.get("message", "Could not generate drafts.")
    )


def save_drafts(job_post, application_form):

    return send_backend_event({
        "type": "update_drafts",
        "job_post": job_post,
        "application_form": application_form
    })


def approve_job_post(job_post, application_form):

    return send_backend_event({
        "type": "approve_job_post",
        "job_post": job_post,
        "application_form": application_form
    })


def approve_application_form(job_post, application_form):

    return send_backend_event({
        "type": "approve_application_form",
        "job_post": job_post,
        "application_form": application_form
    })


# ------------------------------------------------
# 4. READ THE LATEST EDITED JSON
# ------------------------------------------------

def get_edited_drafts():

    try:

        updated_job_post = json.loads(
            st.session_state.job_post_editor
        )

        updated_application_form = json.loads(
            st.session_state.application_form_editor
        )

        if not isinstance(updated_job_post, dict):
            raise ValueError(
                "Job post JSON must be an object."
            )

        if not isinstance(updated_application_form, dict):
            raise ValueError(
                "Application form JSON must be an object."
            )

        return updated_job_post, updated_application_form

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Invalid JSON. Please check the format: {error}"
        )


# ------------------------------------------------
# 5. HEADER
# ------------------------------------------------

st.title("💼📑 Job Post Generator")

st.write(
    "Enter job requirements and let AI generate "
    "a job post and candidate application form."
)

st.divider()


# ------------------------------------------------
# 6. INITIAL JOB REQUIREMENTS
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

            st.warning(
                "Please enter job requirements."
            )

        else:

            with st.spinner(
                "AI is generating both drafts..."
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

                    # Store generated job post
                    st.session_state.job_post = (
                        result["job_post"]
                    )

                    # Store generated application form
                    st.session_state.application_form = (
                        result["application_form"]
                    )

                    # Convert dictionaries into editable JSON text
                    st.session_state.job_post_editor = json.dumps(
                        result["job_post"],
                        indent=4,
                        ensure_ascii=False
                    )

                    st.session_state.application_form_editor = json.dumps(
                        result["application_form"],
                        indent=4,
                        ensure_ascii=False
                    )

                    st.session_state.job_post_approved = False
                    st.session_state.application_form_approved = False
                    st.session_state.drafts_saved = True

                    st.session_state.approved_payload = None
                    st.session_state.saved_file = None

                    st.success(
                        "Both drafts generated successfully!"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Could not generate drafts: {error}"
                    )


# ------------------------------------------------
# 7. DISPLAY GENERATED DRAFTS
# ------------------------------------------------

if (
    st.session_state.job_post
    and st.session_state.application_form
):

    st.success(
        "Both AI-generated drafts are ready for review."
    )

    # ---------------------------------------------
    # JOB POST
    # ---------------------------------------------

    st.subheader("1. Job Description")

    st.text_area(
        "Edit Job Post JSON",
        key="job_post_editor",
        height=350
    )

    st.markdown("**Job Post Preview**")

    st.markdown(
        f"### {st.session_state.job_post.get('job_title', 'Job Title')}"
    )

    st.write(
        st.session_state.job_post.get("role_summary", "")
    )

    st.markdown("**Responsibilities**")

    for item in st.session_state.job_post.get(
        "responsibilities", []
    ):
        st.markdown(f"- {item}")

    st.markdown("**Required Skills**")

    for skill in st.session_state.job_post.get(
        "required_skills", []
    ):
        st.markdown(f"- {skill}")

    if st.session_state.job_post_approved:
        st.success("Job post approved.")
    else:
        st.info("Job post approval pending.")

    st.divider()

    # ---------------------------------------------
    # APPLICATION FORM
    # ---------------------------------------------

    st.subheader("2. Candidate Application Form")

    st.text_area(
        "Edit Application Form JSON",
        key="application_form_editor",
        height=350
    )

    st.markdown("**Application Form Preview**")

    st.markdown(
        f"**{st.session_state.application_form.get('form_title', 'Application Form')}**"
    )

    for index, question in enumerate(
        st.session_state.application_form.get("questions", []),
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

    # ---------------------------------------------
    # SAVE BOTH DRAFTS
    # ---------------------------------------------

    st.divider()

    st.subheader("3. Save Drafts")

    if st.button(
        "Save Both Drafts",
        use_container_width=True
    ):

        try:

            updated_job_post, updated_application_form = (
                get_edited_drafts()
            )

            result = save_drafts(
                updated_job_post,
                updated_application_form
            )

            if result.get("type") != "drafts_updated":
                raise RuntimeError(
                    result.get(
                        "message",
                        "Could not save drafts."
                    )
                )

            st.session_state.job_post = updated_job_post
            st.session_state.application_form = updated_application_form

            st.session_state.job_post_approved = (
                result.get("job_post_approved", False)
            )

            st.session_state.application_form_approved = (
                result.get("application_form_approved", False)
            )

            st.session_state.drafts_saved = True

            st.session_state.approved_payload = None
            st.session_state.saved_file = None

            st.success(
                "Both edited drafts saved successfully."
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Could not save drafts: {error}"
            )

    # ---------------------------------------------
    # APPROVAL SECTION
    # ---------------------------------------------

    st.divider()

    st.subheader("4. Approval Section")

    st.write(
        "Each approval button automatically sends "
        "the latest edited versions to the backend."
    )

    # Approve Job Post
    if st.button(
        "Approve Job Post",
        disabled=st.session_state.job_post_approved,
        use_container_width=True
    ):

        try:

            updated_job_post, updated_application_form = (
                get_edited_drafts()
            )

            result = approve_job_post(
                updated_job_post,
                updated_application_form
            )

            if result.get("type") == "error":
                raise RuntimeError(result.get("message"))

            if result.get("type") != "approval":
                raise RuntimeError(
                    "Unexpected approval response."
                )

            st.session_state.job_post = updated_job_post
            st.session_state.application_form = updated_application_form

            st.session_state.job_post_approved = (
                result.get("job_post_approved", False)
            )

            st.session_state.application_form_approved = (
                result.get("application_form_approved", False)
            )

            st.session_state.approved_payload = (
                result.get("approved_payload")
            )

            st.session_state.saved_file = (
                result.get("saved_file")
            )

            st.success(result.get("message"))

            st.rerun()

        except Exception as error:

            st.error(
                f"Job post approval failed: {error}"
            )

    # Approve Application Questions
    if st.button(
        "Approve Application Questions",
        disabled=st.session_state.application_form_approved,
        use_container_width=True
    ):

        try:

            updated_job_post, updated_application_form = (
                get_edited_drafts()
            )

            result = approve_application_form(
                updated_job_post,
                updated_application_form
            )

            if result.get("type") == "error":
                raise RuntimeError(result.get("message"))

            if result.get("type") != "approval":
                raise RuntimeError(
                    "Unexpected approval response."
                )

            st.session_state.job_post = updated_job_post
            st.session_state.application_form = updated_application_form

            st.session_state.job_post_approved = (
                result.get("job_post_approved", False)
            )

            st.session_state.application_form_approved = (
                result.get("application_form_approved", False)
            )

            st.session_state.approved_payload = (
                result.get("approved_payload")
            )

            st.session_state.saved_file = (
                result.get("saved_file")
            )

            st.success(result.get("message"))

            st.rerun()

        except Exception as error:

            st.error(
                f"Application form approval failed: {error}"
            )

    # ---------------------------------------------
    # FINAL APPROVAL STATUS
    # ---------------------------------------------

    st.divider()

    st.subheader("5. Final Approval Status")

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
            "Both drafts are approved!"
        )

        if st.session_state.saved_file:

            st.write("Combined JSON saved successfully.")

            st.code(
                st.session_state.saved_file,
                language="text"
            )

        if st.session_state.approved_payload:

            st.markdown("**Combined JSON Output**")

            st.json(
                st.session_state.approved_payload
            )


# ------------------------------------------------
# 8. START A NEW JOB POST
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

    st.session_state.approved_payload = None
    st.session_state.saved_file = None

    st.rerun()
