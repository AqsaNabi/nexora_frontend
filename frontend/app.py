import streamlit as st
from chatbot_recruitment import chatbot_recruitment_function
from  detail_dashboard import detail_dashboard_function
# Configure page at the root app entry
st.set_page_config(
    page_title="Nexora Enterprise Portal",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
if "page" not in st.session_state:
    st.session_state.page = "login"
 
# Protect internal pages: require token or redirect to login
public_pages = ["login", "register"]
if st.session_state.page not in public_pages and not st.session_state.get("token"):
    st.session_state.page = "login"
 
# Router
current_page = st.session_state.page
 
if current_page == "register":
    from register import register
    register()
 
elif current_page == "login":
    from login import login
    login()
 
elif current_page == "dashboard":
    from dashboard import dashboard
    dashboard()
 
elif current_page == "employees":
    from employee import employee
    employee()
 
elif current_page in ["events", "announcement"]:
    from announcement import announcement
    announcement()
 
elif current_page in ["policies", "policy"]:
    from policy import policies
    policies()
 
elif current_page == "user_dashboard":
    from user_dashboard import user_dashboard
    user_dashboard()

elif st.session_state.page=="job_applicants":
    detail_dashboard_function()
elif st.session_state.page=="recruitment":
    chatbot_recruitment_function()
else:
    st.session_state.page = "login"
    st.rerun()