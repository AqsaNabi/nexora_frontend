import streamlit as st
def dashboard():
    
 
# -----------------------------------
# 1. Page configuration
# -----------------------------
    st.set_page_config(
        page_title="Nexora | HR Dashboard",
        page_icon="🏢",
        layout="wide"
    )
    
    # -----------------------------------
    # 2. Session state
    # -----------------------------------
    

    
    # -----------------------------------
    # 3. Sidebar
    # -----------------------------------
    
    
    if st.session_state.designation == "HR".lower():
        st.sidebar.title("HR Dashboard")
        st.sidebar.image(st.session_state.profile_picture, width=100)
        st.sidebar.write(f"**{st.session_state.full_name}**")
        
        if st.sidebar.button("Sign out", type="primary"):
            st.session_state.page = "login"
            st.rerun()
        
        # -----------------------------------
        # 4. Styling
        # -----------------------------------
        
        st.markdown(
            """
            <style>
        
            .dashboard-heading {
                font-size: 31px;
                font-weight: 700;
                margin-bottom: 5px;
            }
        
            .dashboard-subheading {
                font-size: 15px;
                opacity: 0.65;
                margin-bottom: 25px;
            }
        
            .dashboard-card {
                background: var(--secondary-background-color);
                border: 1px solid rgba(128,128,128,0.20);
                border-radius: 15px;
                padding: 23px;
                min-height: 205px;
                margin-bottom: 12px;
            }
        
            .card-icon {
                font-size: 30px;
                margin-bottom: 12px;
            }
        
            .card-title {
                font-size: 19px;
                font-weight: 650;
                margin-bottom: 9px;
            }
        
            .card-description {
                font-size: 13px;
                line-height: 1.6;
                opacity: 0.65;
                min-height: 42px;
            }
        
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # -----------------------------------
        # 5. Dashboard home
        # -----------------------------------
        
        
        
        st.markdown(
                '<div class="dashboard-heading">Human Resource Management</div>',
                unsafe_allow_html=True
            )
        
        st.markdown(
                """
                <div class="dashboard-subheading">
                    Manage your workforce, recruitment, company policies
                    and organizational announcements from one place.
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with st.container(border=True):
        
                st.caption(
                    "Select a module to manage your organization's HR activities."
                )
        
                st.write("")
        
                col1, col2 = st.columns(2, gap="large")
        
                # Total employees
                with col1:
        
                    st.markdown(
                        """
                        <div class="dashboard-card">
                            <div class="card-icon">👥</div>
                            <div class="card-title">Total Employees</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
                    if st.button(
                        "View Employees →",
                        key="employees",
                        type="primary",
                        use_container_width=True
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
                                Create company events, announcements
                                and employee notifications.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
                    if st.button(
                        "Create Announcement →",
                        key="events",
                        type="primary",
                        use_container_width=True
                    ):
                        st.session_state.page = "events"
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
                                Create and manage company rules,
                                employee guidelines and HR policies.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
                    if st.button(
                        "Manage Policies →",
                        key="policies",
                        type="primary",
                        use_container_width=True
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
                        unsafe_allow_html=True
                    )
        
                    if st.button(
                        "Manage Recruitment →",
                        key="recruitment",
                        type="primary",
                        use_container_width=True
                    ):
                        st.session_state.page = "recruitment"
                        st.rerun()
        
        # -----------------------------------
        # 6. Footer
        # -----------------------------------
        
        st.write("")
        st.caption("Nexora HR Management System")
        
        