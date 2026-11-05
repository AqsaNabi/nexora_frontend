import streamlit as st
from register import register
from login import login
from dashboard import dashboard
from employee import employee

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



