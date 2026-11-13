
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
# 3. HEADER
# =========================================================

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


# =========================================================
# 4. FETCH DASHBOARD DATA
# =========================================================

dashboard_data = None

try:

    response = requests.get(
        f"{API_URL}/api/ats/dashboard",
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()
    dashboard_data = response.json()

except requests.exceptions.RequestException as error:

    st.error(f"Unable to fetch dashboard data: {error}")

except ValueError:

    st.error("Dashboard API returned an invalid JSON response.")


if dashboard_data is None:

    st.warning(
        "Please make sure the backend server is running "
        "and try refreshing the page."
    )

    st.stop()


jobs = []

if isinstance(dashboard_data, list):

    jobs = dashboard_data

elif isinstance(dashboard_data, dict):

    for key in ["jobs", "job_posts", "recruitment_posts", "data"]:

        value = dashboard_data.get(key)

        if isinstance(value, list):

            jobs = value
            break


if not jobs:

    st.info("No job postings are currently available.")
    st.stop()


# =========================================================
# 5. DASHBOARD OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-heading">Dashboard Overview</div>',
    unsafe_allow_html=True
)

total_applications = 0

for job in jobs:

    post_id = job.get("post_id")

    if post_id is not None:

        try:

            response = requests.get(
                f"{API_URL}/api/ats/jobs/{post_id}/applications",
                timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()
            applications_response = response.json()

            job_applications = []

            if isinstance(applications_response, list):

                job_applications = applications_response

            elif isinstance(applications_response, dict):

                for key in ["applications", "candidates", "data"]:

                    value = applications_response.get(key)

                    if isinstance(value, list):

                        job_applications = value
                        break

            total_applications += len(job_applications)

        except requests.exceptions.RequestException:

            pass

        except ValueError:

            pass


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
# 6. SELECT JOB POSTING
# =========================================================

st.markdown(
    '<div class="section-heading">Select Job Posting</div>',
    unsafe_allow_html=True
)

job_options = {}

for index, job in enumerate(jobs):

    post_id = job.get("post_id")
    job_title = job.get("job_title")

    if post_id is not None:

        if job_title and str(job_title).strip():

            dropdown_label = str(job_title).strip()

        else:

            dropdown_label = (
                f"Job title missing for Post ID: {post_id}"
            )

        # Handle duplicate job titles
        if dropdown_label in job_options:

            dropdown_label = f"{dropdown_label} ({index + 1})"

        job_options[dropdown_label] = post_id


if not job_options:

    st.error("No valid job postings were returned by the backend.")
    st.stop()


selected_job_label = st.selectbox(
    "Choose a job",
    options=list(job_options.keys())
)

selected_post_id = job_options[selected_job_label]

selected_job = {}

for job in jobs:

    if str(job.get("post_id")) == str(selected_post_id):

        selected_job = job
        break


# =========================================================
# 7. JOB INFORMATION
# =========================================================

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
    "created_at",
    "Not available"
)

if generated_date != "Not available" and generated_date:

    generated_date = str(generated_date).split("T")[0]


form_url = selected_job.get(
    "form_url",
    ""
)

with st.container(border=True):

    st.markdown("**Job Post**")

    st.subheader(str(job_title))

    st.divider()

    st.markdown("**Date**")

    st.write(str(generated_date))

    st.markdown("**Job Description**")

    st.write(str(job_description))


# =========================================================
# 8. APPLICATION FORM
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
# 9. AI CANDIDATE EVALUATION
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
# 10. CANDIDATE APPLICATIONS
# =========================================================

st.markdown(
    '<div class="section-heading">Candidate Applications</div>',
    unsafe_allow_html=True
)

applications_response = None

try:

    response = requests.get(
        f"{API_URL}/api/ats/jobs/{selected_post_id}/applications",
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()
    applications_response = response.json()

except requests.exceptions.RequestException as error:

    st.error(f"Unable to fetch candidate applications: {error}")

except ValueError:

    st.error("Applications API returned an invalid JSON response.")


if applications_response is not None:

    applications = []

    if isinstance(applications_response, list):

        applications = applications_response

    elif isinstance(applications_response, dict):

        for key in ["applications", "candidates", "data"]:

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

                candidate_score = application.get("candidate_score")

                if candidate_score is None:

                    formatted_score = "N/A"

                else:

                    try:

                        formatted_score = (
                            f"{float(candidate_score):.2f}%"
                        )

                    except (ValueError, TypeError):

                        formatted_score = str(candidate_score)


                table_data.append({

                    "Candidate Name": application.get(
                        "full_name",
                        "N/A"
                    ),

                    "Phone": application.get(
                        "phone",
                        "N/A"
                    ),

                    "Email": application.get(
                        "email",
                        "N/A"
                    ),

                    "Resume": application.get(
                        "resume_filename",
                        "Not available"
                    ),

                    "AI Match Score": formatted_score

                })


            applications_df = pd.DataFrame(table_data)

            st.dataframe(
                applications_df.style.map(
                    lambda score: (
                        "color: green; font-weight: bold"
                        if isinstance(score, str)
                        and score.endswith("%")
                        else ""
                    ),
                    subset=["AI Match Score"]
                ),
                use_container_width=True,
                hide_index=True
            )


        else:

            st.info("No candidates match your search.")


    else:

        st.info(
            "No applications have been submitted for this job yet."
        )


# =========================================================
# 11. FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        © CyberX Infosystem | Talent Acquisition System 2026
    </div>
    """,
    unsafe_allow_html=True
)
