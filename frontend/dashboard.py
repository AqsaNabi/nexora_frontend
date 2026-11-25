from html import escape

import streamlit as st
from api import api_request


def _get_employee_count():
    try:
        response = api_request("GET", "/count", timeout=10)
        if response.status_code == 200:
            return response.json().get("count", 0)
    except Exception:
        pass

    return None


def dashboard():
    user_role = str(st.session_state.get("designation", "")).strip().lower()

    if user_role not in ["hr", "human resources", "admin", "hr manager"]:
        st.session_state.page = "user_dashboard"
        st.rerun()
        return

    st.html("""
        <style>
        [data-testid="stSidebarContent"] {
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow-y: auto;
        }

        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarUserContent"]
            [data-testid="stLayoutWrapper"]:has(.st-key-hr_sidebar),
        [data-testid="stSidebarUserContent"]
            [data-testid="stVerticalBlock"]:has(.st-key-hr_sidebar) {
            display: flex;
            flex-direction: column;
            flex: 1 0 auto;
        }

        [data-testid="stSidebarUserContent"] .st-key-hr_sidebar,
        .st-key-hr_sidebar > [data-testid="stVerticalBlock"] {
            display: flex;
            flex-direction: column;
            flex: 1 0 auto;
            min-height: calc(100dvh - 7rem);
        }

        .st-key-hr_sidebar > [data-testid="stVerticalBlock"]
            > [data-testid="stLayoutWrapper"]:has(.st-key-hr_sign_out),
        .st-key-hr_sidebar > [data-testid="stVerticalBlock"]
            > .st-key-hr_sign_out,
        .st-key-hr_sidebar > [data-testid="stLayoutWrapper"]:has(.st-key-hr_sign_out),
        .st-key-hr_sidebar > .st-key-hr_sign_out {
            margin-top: auto;
            padding-top: 24px;
        }

        .st-key-hr_profile_photo [data-testid="stImage"] img {
            display: block;
            width: 112px;
            max-width: 100%;
            height: auto;
            aspect-ratio: 1 / 1;
            object-fit: cover;
            object-position: center;
            border-radius: 50%;
            border: 0;
        }

        .hr-profile-details {
            width: 100%;
            text-align: center;
            overflow-wrap: anywhere;
        }

        .hr-profile-name {
            margin: 0;
            font-weight: 700;
        }

        .hr-profile-department {
            margin: 4px 0 0;
            font-size: 0.875rem;
            opacity: 0.7;
        }

        .dashboard-heading {
            font-size: 31px;
            font-weight: 700;
            color: #17365d;
            margin-bottom: 5px;
        }

        .dashboard-subheading {
            font-size: 15px;
            opacity: 0.75;
            margin-bottom: 25px;
        }

        .dashboard-card {
            background: white;
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 15px;
            padding: 23px;
            min-height: 210px;
            box-sizing: border-box;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .card-icon {
            font-size: 30px;
            margin-bottom: 10px;
        }

        .card-title {
            font-size: 19px;
            font-weight: 650;
            color: #17365d;
            margin-bottom: 6px;
        }

        .card-description {
            font-size: 13px;
            line-height: 1.6;
            color: #555;
            min-height: 40px;
        }

        .card-badge {
            display: inline-block;
            background: #EEF2FF;
            color: #3730A3;
            font-size: 13px;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 12px;
            margin-top: 8px;
        }
        </style>
    """)

    with st.sidebar:
        with st.container(key="hr_sidebar"):
            st.title("HR Dashboard")

            profile_picture = st.session_state.get("profile_picture")
            if profile_picture:
                try:
                    with st.container(
                        key="hr_profile_photo",
                        horizontal=True,
                        horizontal_alignment="center",
                    ):
                        st.image(profile_picture, width=112)
                except Exception:
                    pass

            full_name = escape(
                str(st.session_state.get("full_name", "HR Administrator"))
            )
            st.html(f"""
                <div class="hr-profile-details">
                    <div class="hr-profile-name">{full_name}</div>
                    <div class="hr-profile-department">Human Resources Department</div>
                </div>
            """)

            st.divider()

            if st.button(
                " Sign out",
                key="hr_sign_out",
                type="primary",
                use_container_width=True,
            ):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]

                st.session_state.page = "login"
                st.rerun()

    st.html(
        '<div class="dashboard-heading">Human Resource Management</div>'
    )

    st.html("""
        <div class="dashboard-subheading">
            Manage your workforce, recruitment, company policies
            and organizational announcements from one central place.
        </div>
    """)

    emp_count = _get_employee_count()
    count_badge = (
        f'<div class="card-badge">{emp_count} Registered</div>'
        if emp_count is not None
        else ""
    )

    with st.container(border=True):
        st.caption("Select a module to manage your organization's HR activities.")
        st.write("")

        col1, col2 = st.columns(2, gap="large")

        # Total employees.
        with col1:
            st.html(f"""
                <div class="dashboard-card">
                    <div class="card-icon">👥</div>
                    <div class="card-title">Total Employees</div>
                    <div class="card-description">
                        View employee directory, roles, and organizational structure.
                    </div>
                    {count_badge}
                </div>
            """)

            if st.button(
                "View Employees →",
                key="btn_employees",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.page = "employees"
                st.rerun()

        # Events and announcements.
        with col2:
            st.html("""
                <div class="dashboard-card">
                    <div class="card-icon">📢</div>
                    <div class="card-title">Events &amp; Announcements</div>
                    <div class="card-description">
                        Create company events, AI announcements,
                        and distribute email notifications to staff.
                    </div>
                </div>
            """)

            if st.button(
                "Create Announcement →",
                key="btn_events",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.page = "announcement"
                st.rerun()

        st.write("")
        col3, col4 = st.columns(2, gap="large")

        # Policies.
        with col3:
            st.html("""
                <div class="dashboard-card">
                    <div class="card-icon">📚</div>
                    <div class="card-title">Update Policies</div>
                    <div class="card-description">
                        Upload company guidelines, rules, and documents to update
                        the employee policy knowledge base.
                    </div>
                </div>
            """)

            if st.button(
                "Manage Policies →",
                key="btn_policies",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.page = "policies"
                st.rerun()

        # Recruitment.
        with col4:
            st.html("""
                <div class="dashboard-card">
                    <div class="card-icon">💼</div>
                    <div class="card-title">Recruitment</div>
                    <div class="card-description">
                        Create job postings, manage vacancies
                        and review candidate applications.
                    </div>
                </div>
            """)

            if st.button(
                "Manage Recruitment →",
                key="btn_recruitment",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.page = "recruitment"
                st.rerun()

        st.write("")
        col5, _ = st.columns(2, gap="large")

        # Jobs and applicants.
        with col5:
            st.html("""
                <div class="dashboard-card">
                    <div class="card-icon">📋</div>
                    <div class="card-title">Jobs &amp; Applicants</div>
                    <div class="card-description">
                        View available jobs and review applicant information.
                    </div>
                </div>
            """)

            if st.button(
                "View Jobs / Applicants →",
                key="btn_jobs_applicants",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.page = "job_applicants"
                st.rerun()
                # Replace this message with the function call when provided.
                st.info("The Jobs and Applicants module will be connected here.")

    st.write("")
    st.caption("Nexora HR Management System ")
 
 
if __name__ == "__main__":
    st.set_page_config(
        page_title="Nexora | HR Dashboard",
        page_icon="🏢",
        layout="wide",
    )
    dashboard()