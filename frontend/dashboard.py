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
    # Enforce role-based access
    user_role = str(st.session_state.get("designation", "")).strip().lower()
    if user_role not in ["hr", "human resources", "admin", "hr manager"]:
        st.session_state.page = "user_dashboard"
        st.rerun()
        return

    # Sidebar
    st.sidebar.title("HR Dashboard")

    profile_picture = st.session_state.get("profile_picture")
    if profile_picture:
        try:
            st.sidebar.image(profile_picture, width=100)
        except Exception:
            pass

    full_name = st.session_state.get("full_name", "HR Administrator")
    st.sidebar.write(f"**{full_name}**")
    st.sidebar.caption("Human Resources Department")

    st.sidebar.divider()

    if st.sidebar.button("🚪 Sign out", type="primary", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.session_state.page = "login"
        st.rerun()

    # Styling
    st.markdown(
        """
        <style>
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
            border: 1px solid rgba(128,128,128,0.20);
            border-radius: 15px;
            padding: 23px;
            min-height: 180px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
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
        """,
        unsafe_allow_html=True,
    )

    # Dashboard header
    st.markdown(
        '<div class="dashboard-heading">Human Resource Management</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="dashboard-subheading">
            Manage your workforce, recruitment, company policies
            and organizational announcements from one central place.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Live employee count
    emp_count = _get_employee_count()
    count_badge = f'<div class="card-badge">{emp_count} Registered</div>' if emp_count is not None else ""

    with st.container(border=True):
        st.caption("Select a module to manage your organization's HR activities.")
        st.write("")

        col1, col2 = st.columns(2, gap="large")

        # Total employees
        with col1:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="card-icon">👥</div>
                    <div class="card-title">Total Employees</div>
                    <div class="card-description">
                        View employee directory, roles, and organizational structure.
                    </div>
                    {count_badge}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "View Employees →",
                key="btn_employees",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.page = "employees"
                st.rerun()

        # Events and announcements
        with col2:
            st.markdown(
                """
                <div class="dashboard-card">
                    <div class="card-icon">📢</div>
                    <div class="card-title">Events & Announcements</div>
                    <div class="card-description">
                        Create company events, AI announcements,
                        and distribute email notifications to staff.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

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

        # Policies
        with col3:
            st.markdown(
                """
                <div class="dashboard-card">
                    <div class="card-icon">📚</div>
                    <div class="card-title">Update Policies</div>
                    <div class="card-description">
                        Upload company guidelines, rules, and documents to update
                        the employee policy knowledge base.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Manage Policies →",
                key="btn_policies",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.page = "policies"
                st.rerun()

        # Recruitment
        with col4:
            st.markdown(
                """
                <div class="dashboard-card">
                    <div class="card-icon">💼</div>
                    <div class="card-title">Recruitment</div>
                    <div class="card-description">
                        Create job postings, manage vacancies
                        and review candidate applications.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Manage Recruitment →",
                key="btn_recruitment",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.page = "recruitment"
                st.rerun()

    st.write("")
    st.caption("Nexora HR Management System | Powered by Salif Backend")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Nexora | HR Dashboard",
        page_icon="🏢",
        layout="wide",
    )
    dashboard()
