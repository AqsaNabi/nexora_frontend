
import streamlit as st
import requests
import pandas as pd


# =========================================================
# 1. CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8001"
REQUEST_TIMEOUT = 30

st.set_page_config(
    page_title="Talent Dashboard",
    page_icon="👥",
    layout="wide"
)


# =========================================================
# 2. CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(135deg, #f8fbff 0%, #eef4ff 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        min-height: 100vh;
    }

    .ta-header {
        background: linear-gradient(110deg, #172554, #1d4ed8, #6d28d9);
        padding: 25px 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        text-align: left;
    }

    .ta-title {
        color: white;
        font-size: 30px;
        font-weight: 800;
        margin: 0;
    }

    .ta-subtitle {
        color: #DBEAFE;
        font-size: 14px;
        margin-top: 7px;
    }

    .section-heading {
        color: #1e3a8a;
        font-size: 21px;
        font-weight: 750;
        margin-top: 15px;
        margin-bottom: 12px;
    }

    .metric-card {
        background: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #dbeafe;
        box-shadow: 0 2px 8px rgba(30, 64, 175, 0.06);
    }

    .metric-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
    }

    .metric-value {
        color: #1e3a8a;
        font-size: 27px;
        font-weight: 800;
        margin-top: 5px;
    }

    .application-form-btn {
        display: inline-block;
        background: linear-gradient(110deg, #2563eb, #7c3aed);
        color: white !important;
        padding: 11px 20px;
        border-radius: 9px;
        text-decoration: none !important;
        font-weight: 700;
        font-size: 14px;
        margin-top: 8px;
    }

    .application-form-btn:hover {
        background: linear-gradient(110deg, #1d4ed8, #6d28d9);
        color: white !important;
        text-decoration: none !important;
    }

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 12px;
        padding: 25px 0 5px 0;
        margin-top: 30px;
        width: 100%;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #dbeafe;
        padding: 15px;
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 3. HELPER FUNCTIONS
# =========================================================

def get_value(data, *keys, default=None):

    if not isinstance(data, dict):
        return default

    for key in keys:

        if key in data and data[key] is not None:
            return data[key]

    return default


def extract_list(response_data, *possible_keys):

    if isinstance(response_data, list):
        return response_data

    if isinstance(response_data, dict):

        for key in possible_keys:

            value = response_data.get(key)

            if isinstance(value, list):
                return value

    return []


def format_score(score):

    if score is None:
        return "N/A"

    try:
        return f"{float(score):.2f}%"

    except (ValueError, TypeError):
        return str(score)


# =========================================================
# 4. API CALL FUNCTIONS
# =========================================================

def get_dashboard_data():

    try:

        response = requests.get(
            f"{API_URL}/api/ats/dashboard",
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as error:

        st.error(f"Unable to fetch dashboard data: {error}")
        return None

    except ValueError:

        st.error("Dashboard API returned an invalid JSON response.")
        return None


def get_applications(post_id):

    try:

        response = requests.get(
            f"{API_URL}/api/ats/jobs/{post_id}/applications",
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as error:

        st.error(f"Unable to fetch candidate applications: {error}")
        return None

    except ValueError:

        st.error("Applications API returned an invalid JSON response.")
        return None


# =========================================================
# 5. HEADER
# =========================================================
# =========================================================
# 5. HEADER
# =========================================================

st.markdown(
    """
    <style>
    .ta-header {
        background: linear-gradient(110deg, #172554, #1d4ed8, #6d28d9);
        padding: 25px 30px;
        border-radius: 15px;
        margin-bottom: 25px;
    }

    .ta-title {
        color: white;
        font-size: 30px;
        font-weight: 800;
    }

    .ta-subtitle {
        color: #DBEAFE;
        font-size: 14px;
        margin-top: 7px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
#========================================
# 6. FETCH DASHBOARD DATA
# =========================================================

dashboard_data = get_dashboard_data()

if dashboard_data is None:

    st.warning(
        "Please make sure the backend server is running "
        "and try refreshing the page."
    )

    st.stop()


jobs = extract_list(
    dashboard_data,
    "jobs",
    "job_posts",
    "recruitment_posts",
    "data"
)

if not jobs:

    st.info("No job postings are currently available.")

    st.stop()


# =========================================================
# 7. DASHBOARD OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-heading">Dashboard Overview</div>',
    unsafe_allow_html=True
)

total_applications = 0

for job in jobs:

    post_id = get_value(
        job,
        "post_id",
        "id"
    )

    if post_id is not None:

        applications_response = get_applications(post_id)

        if applications_response is not None:

            job_applications = extract_list(
                applications_response,
                "applications",
                "candidates",
                "data"
            )

            total_applications += len(job_applications)


metric1, metric2 = st.columns(2)

with metric1:

    st.metric(
        "Total Job Posts",
        len(jobs)
    )

with metric2:

    st.metric(
        "Total Applicants",
        total_applications
    )


# =========================================================
# 8. SELECT JOB POSTING
# =========================================================

st.markdown(
    '<div class="section-heading">Select Job Posting</div>',
    unsafe_allow_html=True
)

job_options = {}

for job in jobs:

    post_id = get_value(
        job,
        "post_id",
        "id"
    )

    if post_id is None:
        continue

    job_title = get_value(
        job,
        "job_title",
        "title",
        "position",
        default=f"Job {post_id}"
    )

    job_options[str(job_title)] = post_id


if not job_options:

    st.error("No valid job postings were returned by the backend.")

    st.stop()


selected_job_label = st.selectbox(
    "Choose a job",
    options=list(job_options.keys())
)

selected_post_id = job_options[selected_job_label]

post_id_key = str(selected_post_id)

selected_job = next(
    (
        job for job in jobs
        if str(get_value(job, "post_id", "id")) == post_id_key
    ),
    {}
)


# =========================================================
# 9. JOB INFORMATION
# =========================================================

st.markdown(
    '<div class="section-heading">Job Information</div>',
    unsafe_allow_html=True
)

job_title = get_value(
    selected_job,
    "job_title",
    "title",
    "position",
    default="Untitled Job"
)

job_description = get_value(
    selected_job,
    "job_description",
    "description",
    "job_post",
    default="No job description available."
)

generated_date = get_value(
    selected_job,
    "generated_date",
    "created_at",
    "date",
    default="Not available"
)

form_url = get_value(
    selected_job,
    "form_url",
    "application_form_url",
    "application_link",
    default=""
)

with st.container(border=True):

    st.markdown("**Job Post**")

    st.subheader(str(job_title))

    st.divider()

    st.markdown("**Generated Date**")

    st.write(str(generated_date))

    st.markdown("**Job Description**")

    st.write(str(job_description))


# =========================================================
# 10. APPLICATION FORM
# =========================================================

st.divider()

st.markdown(
    '<div class="section-heading">Application Form</div>',
    unsafe_allow_html=True
)

if form_url and isinstance(form_url, str):

    if form_url.startswith(("https://", "http://")):

        st.markdown(
            f"""
            <a href="{form_url}"
               target="_blank"
               class="application-form-btn">
                Open Google Form ↗
            </a>
            """,
            unsafe_allow_html=True
        )

    else:

        st.caption("Application form link is not a valid URL.")

else:

    st.caption("Application form link is not available.")


# =========================================================
# 11. AI CANDIDATE EVALUATION
# =========================================================

st.markdown(
    '<div class="section-heading">AI Candidate Evaluation</div>',
    unsafe_allow_html=True
)

st.write(
    "Candidates are evaluated individually against the selected "
    "job description. Their AI match scores are displayed "
    "alongside their application details."
)


# =========================================================
# 12. CANDIDATE APPLICATIONS
# =========================================================

st.markdown(
    '<div class="section-heading">Candidate Applications</div>',
    unsafe_allow_html=True
)

applications_response = get_applications(selected_post_id)

if applications_response is not None:

    applications = extract_list(
        applications_response,
        "applications",
        "candidates",
        "data"
    )

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
                get_value(
                    application,
                    "full_name",
                    "candidate_name",
                    "name",
                    default=""
                )
            )

            email = str(
                get_value(
                    application,
                    "email",
                    default=""
                )
            )

            if (
                search_query.lower() in candidate_name.lower()
                or search_query.lower() in email.lower()
            ):

                filtered_applications.append(application)


        if filtered_applications:

            table_data = []

            for application in filtered_applications:

                table_data.append({

                    "Candidate Name": get_value(
                        application,
                        "full_name",
                        "candidate_name",
                        "name",
                        default="N/A"
                    ),

                    "Phone": get_value(
                        application,
                        "phone",
                        default="N/A"
                    ),

                    "Email": get_value(
                        application,
                        "email",
                        default="N/A"
                    ),

                    "Resume": get_value(
                        application,
                        "resume_filename",
                        "resume_name",
                        default="Not available"
                    ),

                    "AI Match Score": format_score(
                        get_value(
                            application,
                            "ai_score",
                            "match_score",
                            "evaluation_score",
                            "score",
                            default=None
                        )
                    )

                })


            applications_df = pd.DataFrame(table_data)

            st.dataframe(
                applications_df,
                use_container_width=True,
                hide_index=True,
                column_order=[
                    "Candidate Name",
                    "Phone",
                    "Email",
                    "Resume",
                    "AI Match Score"
                ]
            )

        else:

            st.info("No candidates match your search.")

    else:

        st.info(
            "No applications have been submitted for this job yet."
        )


# =========================================================
# 13. FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        © CyberX Infosystem | Talent Acquisition System 2026
    </div>
    """,
    unsafe_allow_html=True
)
