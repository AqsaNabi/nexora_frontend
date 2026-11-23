import streamlit as st
import html
 
from detail_dash_func import (
    fetch_dashboard_data,
    fetch_applications,
    start_websocket,
    notification_queue
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
# MAIN DASHBOARD FUNCTION
# ============================================================
 
def detail_dashboard_function():
 
    # ========================================================
    # BACKEND CONFIGURATION
    # ========================================================
 
    API_URL = "http://127.0.0.1:8000"
 
    # Start WebSocket connection
    token = st.session_state.get("token")
    start_websocket(token)
 
    # ========================================================
    # MAIN ATS DASHBOARD
    # ========================================================
 
    @st.fragment(run_every="30s")
    def render_ats_dashboard():
 
        # ====================================================
        # WEBSOCKET NOTIFICATIONS
        # ====================================================
 
        while not notification_queue.empty():
 
            try:
 
                notification = notification_queue.get_nowait()
 
                if notification.get("type") == "new_application":
 
                    st.toast(
                        notification.get(
                            "message",
                            "A new application has arrived!"
                        ),
                        icon="🔔"
                    )
 
            except Exception:
                break
 
        # ====================================================
        # 1. CUSTOM CSS (ORANGE & WHITE THEME)
        # ====================================================
 
        st.markdown(
            """
            <style>
 
                .stApp {
                    background-color: #FFF8F2; /* Warm off-white */
                    color: #3A2A1E !important; /* Dark warm brown text */
                }
 
                .block-container {
                    padding-top: 2rem;
                    padding-bottom: 2rem;
                    min-height: 100vh;
                }
 
                /* Header */
 
                .ta-header {
                    background: linear-gradient(
                        110deg,
                        #EA580C, /* Deep orange */
                        #F97316, /* Bright orange */
                        #FDBA74  /* Soft peach */
                    );
                    padding: 25px 30px;
                    border-radius: 15px;
                    margin-bottom: 25px;
                    box-shadow: 0 4px 6px rgba(234, 88, 12, 0.15);
                }
 
                .ta-title {
                    color: #ffffff !important;
                    font-size: 30px;
                    font-weight: 800;
                    margin: 0;
                }
 
                .ta-subtitle {
                    color: #FFF3E6 !important;
                    font-size: 14px;
                    margin-top: 7px;
                }
 
                /* Section headings */
 
                .section-heading {
                    color: #C2410C !important; /* Deep orange */
                    font-size: 21px;
                    font-weight: 750;
                    margin-top: 15px;
                    margin-bottom: 12px;
                }
 
                /* Application form button */
 
                .application-form-btn {
                    display: inline-block;
                    background: linear-gradient(
                        110deg,
                        #F97316,
                        #EA580C
                    );
                    color: white !important;
                    padding: 11px 20px;
                    border-radius: 9px;
                    text-decoration: none !important;
                    font-weight: 700;
                    font-size: 14px;
                    margin-top: 8px;
                    transition: all 0.2s ease;
                }
 
                .application-form-btn:hover {
                    background: linear-gradient(
                        110deg,
                        #EA580C,
                        #C2410C
                    );
                    transform: translateY(-1px);
                }
 
                /* Footer */
 
                .footer {
                    text-align: center;
                    color: #9A7B66 !important;
                    font-size: 12px;
                    padding: 25px 0 5px 0;
                    margin-top: 30px;
                    width: 100%;
                }
 
                /* Metric cards */
 
                div[data-testid="stMetric"] {
                    background: #ffffff !important;
                    border: 1px solid #FED7AA;
                    padding: 15px;
                    border-radius: 12px;
                    box-shadow: 0 1px 3px rgba(194, 65, 12, 0.06);
                }
 
                div[data-testid="stMetric"] label,
                div[data-testid="stMetric"] label p {
                    color: #9A7B66 !important;
                }
 
                div[data-testid="stMetric"] [data-testid="stMetricValue"],
                div[data-testid="stMetric"] [data-testid="stMetricValue"] div {
                    color: #C2410C !important;
                }
 
                /* General text visibility */
 
                .stMarkdown p,
                .stMarkdown li,
                .stMarkdown strong,
                .stMarkdown span,
                .stWrite,
                [data-testid="stText"] {
                    color: #3A2A1E;
                }
 
                /* Labels and captions */
 
                .stSelectbox label,
                .stTextInput label,
                .stTextArea label,
                .stMultiSelect label,
                .stDateInput label,
                .stNumberInput label {
                    color: #C2410C !important;
                }
 
                /* Selected dropdown value */
 
                div[data-testid="stSelectbox"] [role="combobox"],
                div[data-testid="stSelectbox"] [role="combobox"] *,
                div[data-testid="stSelectbox"] [data-testid="stMarkdownContainer"],
                div[data-testid="stSelectbox"] [data-testid="stMarkdownContainer"] p {
                    color: #3A2A1E !important;
                    -webkit-text-fill-color: #3A2A1E !important;
                    opacity: 1 !important;
                }
 
                /* Dropdown label */
 
                div[data-testid="stSelectbox"] label,
                div[data-testid="stSelectbox"] label * {
                    color: #C2410C !important;
                    -webkit-text-fill-color: #C2410C !important;
                }
 
                /* Dropdown options */
 
                [data-testid="stSelectboxVirtualDropdown"] li,
                [data-testid="stSelectboxVirtualDropdown"] li *,
                [data-testid="stSelectboxVirtualDropdown"] [role="option"],
                [data-testid="stSelectboxVirtualDropdown"] [role="option"] * {
                    color: #3A2A1E !important;
                    -webkit-text-fill-color: #3A2A1E !important;
                }
 
                /* Job information container */
 
                div[data-testid="stVerticalBlockBorderWrapper"] {
                    color: #3A2A1E !important;
                    border: 1px solid #FED7AA !important;
                    border-radius: 12px;
                }
 
                div[data-testid="stVerticalBlockBorderWrapper"] p,
                div[data-testid="stVerticalBlockBorderWrapper"] strong,
                div[data-testid="stVerticalBlockBorderWrapper"] span {
                    color: #3A2A1E !important;
                }
 
                /* Candidate search input */
 
                input {
                    color: #3A2A1E !important;
                    border-color: #FED7AA !important;
                }
 
                /* Tables */
 
                table {
                    color: #3A2A1E !important;
                }
 
                th {
                    color: #C2410C !important;
                    border-bottom: 2px solid #FED7AA !important;
                }
 
                td {
                    color: #3A2A1E !important;
                }
 
                /* Sidebar CSS */
 
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
                    color: #7C2D12 !important;
                }
 
                [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
                    color: #9A5B3A !important;
                }
 
                [data-testid="stSidebar"] hr {
                    border-color: rgba(194, 65, 12, 0.25) !important;
                }
 
                [data-testid="stSidebar"] div.stButton > button {
                    width: 100%;
                    background: linear-gradient(
                        135deg,
                        #F97316,
                        #EA580C
                    ) !important;
                    color: white !important;
                    border: 1px solid rgba(255,255,255,0.35) !important;
                    border-radius: 11px !important;
                }
 
                [data-testid="stSidebar"] div.stButton > button:hover {
                    background: linear-gradient(
                        135deg,
                        #EA580C,
                        #C2410C
                    ) !important;
                }
 
            </style>
            """,
            unsafe_allow_html=True
        )
 
        # ====================================================
        # 2. HEADER
        # ====================================================
 
        st.markdown(
            '<div class="ta-header">'
            '<div class="ta-title">Talent Acquisition</div>'
            '<div class="ta-subtitle">'
            'Applicant Tracking System | Recruitment Management | '
            'Intelligent Candidate Evaluation'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
 
        # ====================================================
        # 3. FETCH DASHBOARD DATA
        # ====================================================
 
        dashboard_data, dashboard_error = fetch_dashboard_data()
 
        if dashboard_error:
 
            st.error(
                f"Unable to fetch dashboard data: {dashboard_error}"
            )
 
            st.warning(
                "Please make sure the backend server is running "
                "and try refreshing the page."
            )
 
            return
 
        jobs = []
 
        if isinstance(dashboard_data, list):
 
            jobs = dashboard_data
 
        elif isinstance(dashboard_data, dict):
 
            for key in [
                "jobs",
                "job_posts",
                "recruitment_posts",
                "data"
            ]:
 
                value = dashboard_data.get(key)
 
                if isinstance(value, list):
 
                    jobs = value
                    break
 
        if not jobs:
 
            st.info("No job postings are currently available.")
 
        # ====================================================
        # 4. DASHBOARD OVERVIEW
        # ====================================================
 
        st.markdown(
            '<div class="section-heading">Overview</div>',
            unsafe_allow_html=True
        )
 
        total_applications = 0
 
        for job in jobs:
 
            post_id = job.get("post_id")
 
            if post_id is not None:
 
                applications_response, applications_error = (
                    fetch_applications(post_id)
                )
 
                if applications_error is None:
 
                    job_applications = []
 
                    if isinstance(applications_response, list):
 
                        job_applications = applications_response
 
                    elif isinstance(applications_response, dict):
 
                        for key in [
                            "applications",
                            "candidates",
                            "data"
                        ]:
 
                            value = applications_response.get(key)
 
                            if isinstance(value, list):
 
                                job_applications = value
                                break
 
                    total_applications += len(job_applications)
 
        metric1, metric2 = st.columns(2)
 
        with metric1:
            st.metric("Total Job Posts", len(jobs))
 
        with metric2:
            st.metric("Total Applicants", total_applications)
 
        # ====================================================
        # 5. SELECT JOB POSTING
        # ====================================================
 
        st.markdown(
            '<div class="section-heading">Select Job Posting</div>',
            unsafe_allow_html=True
        )
 
        job_options = {}
 
        for index, job in enumerate(jobs):
 
            post_id = job.get("post_id")
            job_title = job.get("job_title")
 
            generated_date = job.get(
                "job_posted_date",
                "Not available"
            )
 
            if post_id is not None:
 
                if job_title and str(job_title).strip():
 
                    job_title = str(job_title).strip()
 
                else:
 
                    job_title = (
                        f"Job title missing for Post ID: {post_id}"
                    )
 
                if generated_date and generated_date != "Not available":
 
                    generated_date = str(generated_date).split("T")[0]
 
                else:
 
                    generated_date = "Date not available"
 
                dropdown_label = (
                    f"{job_title} - {generated_date}"
                )
 
                if dropdown_label in job_options:
 
                    dropdown_label = (
                        f"{dropdown_label} ({index + 1})"
                    )
 
                job_options[dropdown_label] = post_id
 
        selected_post_id = None
        selected_job = {}
 
        if job_options:
 
            selected_job_label = st.selectbox(
                "Choose a job",
                options=list(job_options.keys())
            )
 
            selected_post_id = job_options[selected_job_label]
 
            for job in jobs:
 
                if str(job.get("post_id")) == str(selected_post_id):
 
                    selected_job = job
                    break
 
        else:
 
            st.selectbox(
                "Choose a job",
                options=["No jobs available"],
                disabled=True
            )
 
        # ====================================================
        # 6. JOB INFORMATION
        # ====================================================
 
        st.markdown(
            '<div class="section-heading">Job Information</div>',
            unsafe_allow_html=True
        )
 
        job_title = selected_job.get("job_title")
 
        if not job_title or not str(job_title).strip():
 
            job_title = "Job title not available"
 
        job_description = selected_job.get(
            "job_description",
            "No job description available."
        )
 
        generated_date = selected_job.get(
            "job_posted_date",
            "Not available"
        )
 
        if generated_date != "Not available" and generated_date:
 
            generated_date = str(generated_date).split("T")[0]
 
        form_url = selected_job.get("form_url", "")
 
        with st.container(border=True):
 
            st.markdown("**Job Post**")
 
            st.subheader(str(job_title))
 
            st.divider()
 
            st.markdown("**Date**")
 
            st.write(str(generated_date))
 
            st.markdown("**Job Description**")
 
            st.write(str(job_description))
 
            # Application form URL
 
            application_form_url = (
                form_url
                or "https://docs.google.com/forms/d/e/1FAIpQLScattpxyxoRbIjJGh_LlZrisftpR45giWaKZY2aC7HAmq3jqw/viewform"
            )
 
            st.markdown(
                f"""
                **Application Form**
 
                <a href="{html.escape(str(application_form_url), quote=True)}"
                   target="_blank"
                   rel="noopener noreferrer"
                   class="application-form-btn">
                    Open Google Form ↗
                </a>
                """,
                unsafe_allow_html=True
            )
 
        # ====================================================
        # 7. AI CANDIDATE EVALUATION
        # ====================================================
 
        st.markdown(
            '<div class="section-heading">AI Candidate Evaluation</div>',
            unsafe_allow_html=True
        )
 
        st.write(
            "Candidates are evaluated individually against the selected "
            "job description. Their AI match scores are displayed "
            "alongside their application details."
        )
 
        # ====================================================
        # 8. CANDIDATE APPLICATIONS
        # ====================================================
 
        st.markdown(
            '<div class="section-heading">Candidate Applications</div>',
            unsafe_allow_html=True
        )
 
        applications_response = None
 
        if selected_post_id is not None:
 
            applications_response, applications_error = (
                fetch_applications(selected_post_id)
            )
 
            if applications_error:
 
                st.error(
                    "Unable to fetch candidate applications: "
                    f"{applications_error}"
                )
 
        if selected_post_id is None:
 
            st.metric("Applications for Selected Job", 0)
 
            st.info("No applications are currently available.")
 
        elif applications_response is not None:
 
            applications = []
 
            if isinstance(applications_response, list):
 
                applications = applications_response
 
            elif isinstance(applications_response, dict):
 
                for key in [
                    "applications",
                    "candidates",
                    "data"
                ]:
 
                    value = applications_response.get(key)
 
                    if isinstance(value, list):
 
                        applications = value
                        break
 
            st.metric(
                "Applications for Selected Job",
                len(applications)
            )
 
            if applications:
 
                search_query = st.text_input(
                    "Search candidates by name or email",
                    placeholder="Enter candidate name or email..."
                )
 
                filtered_applications = []
 
                for application in applications:
 
                    candidate_name = str(
                        application.get("full_name", "")
                    )
 
                    email = str(
                        application.get("email", "")
                    )
 
                    if (
                        search_query.lower() in candidate_name.lower()
                        or search_query.lower() in email.lower()
                    ):
 
                        filtered_applications.append(application)
 
                if filtered_applications:
 
                    table_data = []
 
                    for application in filtered_applications:
 
                        candidate_score = application.get(
                            "candidate_score"
                        )
 
                        if candidate_score is None:
 
                            formatted_score = "N/A"
 
                        else:
 
                            try:
 
                                formatted_score = (
                                    f"{float(candidate_score):.2f}%"
                                )
 
                            except (ValueError, TypeError):
 
                                formatted_score = str(candidate_score)
 
                        # Check whether candidate uploaded a resume
 
                        resume_uploaded = bool(
                            application.get("has_resume", False)
                        )
 
                        # Create resume URL
 
                        resume_url = None
 
                        if resume_uploaded:
 
                            application_id = application.get(
                                "application_id"
                            )
 
                            if application_id is not None:
 
                                resume_url = (
                                    f"{API_URL}/api/ats/applications/"
                                    f"{application_id}/resume"
                                )
 
                        table_data.append({
 
                            "Candidate Name": application.get(
                                "full_name", "N/A"
                            ),
 
                            "Phone": application.get(
                                "phone", "N/A"
                            ),
 
                            "Email": application.get(
                                "email", "N/A"
                            ),
 
                            "Resume": resume_url,
 
                            "AI Match Score": formatted_score
 
                        })
 
                    # ============================================
                    # BUILD TABLE WITH CLICKABLE RESUME LINKS
                    # ============================================
 
                    table_html = """
                    <table style="
                        width:100%;
                        border-collapse:collapse;
                        background:white;
                    ">
                    <thead>
                    <tr>
                        <th style="padding:12px;text-align:left;">Candidate Name</th>
                        <th style="padding:12px;text-align:left;">Phone</th>
                        <th style="padding:12px;text-align:left;">Email</th>
                        <th style="padding:12px;text-align:left;">Resume</th>
                        <th style="padding:12px;text-align:left;">AI Match Score</th>
                    </tr>
                    </thead>
                    <tbody>
                    """
 
                    for row in table_data:
 
                        resume_url = row["Resume"]
 
                        if resume_url:
 
                            resume_cell = (
                                f'<a href="{html.escape(resume_url, quote=True)}" '
                                f'target="_blank" rel="noopener noreferrer" '
                                f'style="color:#F97316;font-weight:bold;text-decoration:none;">'
                                f'View PDF</a>'
                            )
 
                        else:
 
                            resume_cell = "None"
 
                        score_style = (
                            "color:#16A34A;font-weight:bold;"
                            if str(row["AI Match Score"]).endswith("%")
                            else ""
                        )
 
                        table_html += "<tr>"
 
                        table_html += (
                            '<td style="padding:12px;border-bottom:1px solid #FED7AA;">'
                            f'{html.escape(str(row["Candidate Name"]))}</td>'
                        )
 
                        table_html += (
                            '<td style="padding:12px;border-bottom:1px solid #FED7AA;">'
                            f'{html.escape(str(row["Phone"]))}</td>'
                        )
 
                        table_html += (
                            '<td style="padding:12px;border-bottom:1px solid #FED7AA;">'
                            f'{html.escape(str(row["Email"]))}</td>'
                        )
 
                        table_html += (
                            '<td style="padding:12px;border-bottom:1px solid #FED7AA;">'
                            f'{resume_cell}</td>'
                        )
 
                        table_html += (
                            f'<td style="padding:12px;border-bottom:1px solid #FED7AA;{score_style}">'
                            f'{html.escape(str(row["AI Match Score"]))}</td>'
                        )
 
                        table_html += "</tr>"
 
                    table_html += """
                    </tbody>
                    </table>
                    """
 
                    st.markdown(
                        table_html,
                        unsafe_allow_html=True
                    )
 
                else:
 
                    st.info("No candidates match your search.")
 
            else:
 
                st.info(
                    "No applications have been submitted for this job yet."
                )
 
        # ====================================================
        # 9. FOOTER
        # ====================================================
 
        st.markdown(
            """
            <div class="footer">
                © CyberX Infosystem | Talent Acquisition System 2026
            </div>
            """,
            unsafe_allow_html=True
        )
 
    # ========================================================
    # RUN SIDEBAR AND DASHBOARD
    # ========================================================
 
    display_sidebar()
 
    render_ats_dashboard()