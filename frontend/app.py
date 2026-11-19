import streamlit as st
from register import register
from login import login
from dashboard import dashboard
from employee import employee
from announcement import announcement
from chatbot_recruitment import chatbot_recruitment_function
from  detail_dashboard import detail_dashboard_function
st.set_page_config(
    page_title="Nexora Enterprise Portal",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)
if "page" not in st.session_state:
    st.session_state.page = "login"



if st.session_state.page == "register":

    register()
elif st.session_state.page == "dashboard":

    dashboard()

elif st.session_state.page == "login":

    login()
elif st.session_state.page == "employees":
    employee()
elif st.session_state.page in ["events", "announcement"]:
    announcement()
elif st.session_state.page=="job_applicants":
    detail_dashboard_function()
elif st.session_state.page=="recruitment":
    chatbot_recruitment_function()


