import os
import requests
import streamlit as st
import base64


FRONTEND_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

LOGO_PATH = os.path.join(
    FRONTEND_DIR,
    "lo.png"
)

API_URL = "http://127.0.0.1:8000"  



def login():

    login_tab, register_tab = st.tabs(
        ["Login", "Register"]
    )

    with login_tab:
        if os.path.exists(LOGO_PATH):
                st.image(
                    LOGO_PATH,
                    width=150
                )

        

        email = st.text_input(
            "Email Address"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button(
            "Sign In",
            type="primary"
        ):

            if email.strip() == "" or password == "":

                st.error(
                    "Please fill in all fields!"
                )

                return

            try:

                response = requests.post(
                    f"{API_URL}/login",
                    json={
                        "email": email.strip(),
                        "password": password
                    }
                )

            except requests.exceptions.RequestException:

                st.error(
                    "Could not connect to the backend."
                )

                return

            if response.status_code == 200:

                data = response.json()

                token = data["access_token"]

                
                
                st.session_state.employee_id = data["employee_id"]
                st.session_state.full_name = data["full_name"]
                st.session_state.email = data["email"]
                st.session_state.designation = data["designation"]
                st.session_state.date_of_birth = data["date_of_birth"]
                st.session_state.gender = data["gender"]
                st.session_state.mobile = data["mobile"]
                st.session_state.teamsmail = data["teamsmail"]
                st.session_state.profile_picture = data["profile_picture"]  
                profile_picture = data.get("profile_picture")

                if profile_picture:
                   st.session_state.profile_picture = base64.b64decode(profile_picture)
                else:
                   st.session_state.profile_picture = None
                # Store token if you need it later
                st.session_state.token = token

                st.session_state.page = "dashboard"

                st.rerun()

            elif response.status_code == 401:

                st.error(
                    "Invalid email or password!"
                )

            elif response.status_code == 422:

                st.error(
                    "Invalid request data!"
                )

            else:

                st.error(
                    f"Login failed: {response.status_code}"
                )
    with register_tab:

        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0 20px 0;">
                <h2 style="margin-bottom: 5px;">Create Your Account</h2>
                <p style="color: #666; font-size: 15px;">
                    Register to get started with the Employee Management System
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:

            if st.button(
                "Register Now",
                type="primary",
                use_container_width=True
            ):

                st.session_state.page = "register"
                st.rerun()

            st.markdown(
                """
                <p style="text-align: center; color: #777; font-size: 13px;">
                    Already have an account? Switch to the Login tab.
                </p>
                """,
                unsafe_allow_html=True
            )