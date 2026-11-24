import os
import base64
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")

FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(FRONTEND_DIR, "lo.png")


def login():
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
        else:
            st.markdown(
                """
                <div style="padding: 10px 0 15px 0;">
                    <h2 style="margin: 0; color: #17365d;"> Nexora Portal</h2>
                    <p style="color: #666; font-size: 14px; margin-top: 4px;">Sign in to your account</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        email = st.text_input("Email Address", placeholder="name@company.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Sign In", type="primary", use_container_width=True):
            if not email.strip() or not password:
                st.error("Please fill in all fields!")
                return

            try:
                with st.spinner("Authenticating..."):
                    response = requests.post(
                        f"{API_URL}/login",
                        json={"email": email.strip(), "password": password},
                        timeout=60,
                    )
            except requests.exceptions.ConnectionError:
                st.error(f"Could not connect to the backend at {API_URL}. Please ensure the server is running.")
                return
            except requests.exceptions.Timeout:
                st.error("Login request timed out. Please try again.")
                return
            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {e}")
                return

            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError:
                    st.error("Invalid response from server.")
                    return

                token = data.get("access_token")
                st.session_state.token = token
                st.session_state.employee_id = data.get("employee_id")
                st.session_state.full_name = data.get("full_name", "")
                st.session_state.email = data.get("email", email.strip())
                st.session_state.designation = data.get("designation", "")
                st.session_state.date_of_birth = data.get("date_of_birth")
                st.session_state.gender = data.get("gender")
                st.session_state.mobile = data.get("mobile")
                st.session_state.teamsmail = data.get("teamsmail")

                # Handle base64 encoded profile picture
                raw_pic = data.get("profile_picture")
                if raw_pic:
                    try:
                        st.session_state.profile_picture = base64.b64decode(raw_pic)
                    except Exception:
                        st.session_state.profile_picture = None
                else:
                    st.session_state.profile_picture = None

                # Role-based redirection
                role = str(data.get("designation", "")).strip().lower()
                if role in ["hr", "human resources", "admin", "hr manager"]:
                    st.session_state.page = "dashboard"
                else:
                    st.session_state.page = "user_dashboard"

                st.rerun()

            elif response.status_code == 401:
                st.error("Invalid email or password!")
            elif response.status_code == 422:
                st.error("Invalid email or password format.")
            else:
                detail = "Login failed"
                try:
                    detail = response.json().get("detail", detail)
                except Exception:
                    pass
                st.error(f"{detail} (Code {response.status_code})")

    with register_tab:
        st.markdown(
            """
            <div style="text-align: center; padding: 15px 0 20px 0;">
                <h2 style="margin-bottom: 5px; color: #17365d;">Create Your Account</h2>
                <p style="color: #666; font-size: 15px;">
                    Register to get started with the Employee Management System
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Register Now", type="primary", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

            st.markdown(
                """
                <p style="text-align: center; color: #777; font-size: 13px; margin-top: 10px;">
                    Already have an account? Use the Login tab above.
                </p>
                """,
                unsafe_allow_html=True,
            )
