import os
from datetime import date
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")

def register():
    col_back, col_space = st.columns([1, 5])
    with col_back:
        if st.button("← Back to Login", type="primary", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

    st.title("👤 Employee Registration")
    st.caption("Create your employee account to join Nexora.")

    with st.form("employee_registration_form"):
        st.subheader("Employee Details")

        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("Full Name *", placeholder="Jane Doe")
            email = st.text_input("Email Address *", placeholder="jane.doe@company.com")
            password = st.text_input("Password * (min 8 characters)", type="password")
            confirm_password = st.text_input("Confirm Password *", type="password")
            designation = st.text_input("Designation *", placeholder="Software Engineer / HR / Manager")

        with col2:
            gender = st.selectbox(
                "Gender *",
                ["Select", "Female", "Male", "Other"],
            )

            date_of_birth = st.date_input(
                "Date of Birth *",
                value=date(2000, 1, 1),
                min_value=date(1940, 1, 1),
                max_value=date.today(),
            )

            mobile = st.text_input("Mobile Number * (10 digits)", max_chars=10, placeholder="9876543210")
            teamsmail = st.text_input("Teams Email (optional)", placeholder="jane.doe@teams.company.com")

            profile_picture = st.file_uploader(
                "Upload Profile Picture (Optional, JPG/PNG, max 10MB)",
                type=["jpg", "jpeg", "png"],
            )

        st.info("ℹ️ Employee ID will be generated automatically upon registration.")

        submit = st.form_submit_button(
            "Submit Registration",
            type="primary",
            use_container_width=True,
        )

    if submit:
        # Client-side validations
        if not full_name.strip():
            st.error("Full name is required.")
        elif len(full_name.strip()) < 2:
            st.error("Full name must be at least 2 characters.")
        elif not email.strip() or "@" not in email or "." not in email.split("@")[-1]:
            st.error("Please enter a valid email address.")
        elif not password:
            st.error("Password is required.")
        elif len(password) < 8:
            st.error("Password must contain at least 8 characters.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif not designation.strip():
            st.error("Designation is required.")
        elif gender == "Select" or gender not in ["Male", "Female", "Other"]:
            st.error("Please select a valid gender.")
        elif date_of_birth >= date.today():
            st.error("Date of birth must be in the past.")
        elif not mobile.isdigit() or len(mobile.strip()) != 10:
            st.error("Mobile number must contain exactly 10 numeric digits.")
        else:
            payload = {
                "full_name": full_name.strip(),
                "email": email.strip().lower(),
                "password": password,
                "designation": designation.strip(),
                "gender": gender,
                "date_of_birth": date_of_birth.isoformat(),
                "mobile": mobile.strip(),
                "teamsmail": teamsmail.strip().lower() if teamsmail else "",
            }

            files = None
            if profile_picture is not None:
                files = {
                    "profile_picture": (
                        profile_picture.name,
                        profile_picture.getvalue(),
                        profile_picture.type or "image/jpeg",
                    )
                }

            try:
                with st.spinner("Submitting registration to server..."):
                    response =requests.post(
                        f"{API_URL}/register",
                        data=payload,
                        files=files,
                        timeout=30
                    )

                if response.status_code in [200, 201]:
                    try:
                        result = response.json()
                        msg = result.get("message", "Employee registered successfully!")
                    except Exception:
                        msg = "Employee registered successfully!"

                    st.success(f"✅ {msg}")
                    st.toast(msg, icon="🎉")
                    st.session_state.page = "login"
                    st.rerun()

                elif response.status_code == 409:
                    st.error("An employee with this email address already exists.")
                elif response.status_code == 413:
                    st.error("Profile picture exceeds the 10 MB size limit.")
                else:
                    detail = "Registration failed."
                    try:
                        detail = response.json().get("detail", detail)
                    except Exception:
                        pass
                    st.error(f"Registration error: {detail} (Status {response.status_code})")

            except requests.exceptions.ConnectionError:
                st.error(f"Cannot connect to backend server at {API_URL}. Please ensure it is running.")
            except requests.exceptions.Timeout:
                st.error("Registration request timed out. Please try again.")
            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {e}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Employee Registration",
        page_icon="👤",
        layout="wide",
    )
    register()
