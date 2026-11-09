 
import streamlit as st
import requests
from datetime import date
 
BACKEND_URL = "http://127.0.0.1:8000/register"
 
 
def register():
 
    st.set_page_config(
        page_title="Employee Registration",
        page_icon="👤",
        layout="wide"
    )
 
    st.title("Employee Registration")
    st.caption("Create your employee account.")
 
    with st.form("employee_registration_form"):
 
        st.subheader("Employee Details")
 
        col1, col2 = st.columns(2)
 
        with col1:
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )
            designation = st.text_input("Designation")
 
        with col2:
            gender = st.selectbox(
                "Gender",
                ["Select", "Female", "Male", "Other"]
            )
 
            date_of_birth = st.date_input(
                "Date of Birth",
                value=date(2000, 1, 1),
                min_value=date(1950, 1, 1),
                max_value=date.today()
            )
 
            mobile = st.text_input("Mobile Number")
            teamsmail = st.text_input("Teams Email")
 
            profile_picture = st.file_uploader(
                "Upload Profile Picture",
                type=["jpg", "jpeg", "png"]
            )
 
        st.info("Employee ID will be generated automatically.")
 
        submit = st.form_submit_button(
            "Submit Registration",
            type="primary",
            width="stretch"
        )
 
    if submit:
 
        if not all([
            full_name.strip(),
            email.strip(),
            password,
            confirm_password,
            designation.strip(),
            mobile.strip(),
            teamsmail.strip()
        ]) or gender == "Select":
 
            st.error("Please fill all required fields.")
 
        elif password != confirm_password:
            st.error("Passwords do not match.")
 
        elif len(password) < 8:
            st.error("Password must contain at least 8 characters.")
 
        elif not mobile.isdigit() or len(mobile) != 10:
            st.error("Mobile number must contain exactly 10 digits.")
 
        elif "@" not in email or "." not in email.split("@")[-1]:
            st.error("Enter a valid email address.")
 
        elif "@" not in teamsmail or "." not in teamsmail.split("@")[-1]:
            st.error("Enter a valid Teams email address.")
 
        else:
 
            payload = {
                "full_name": full_name.strip(),
                "email": email.strip().lower(),
                "password": password,
                "designation": designation.strip(),
                "gender": gender,
                "date_of_birth": date_of_birth.isoformat(),
                "mobile": mobile,
                "teamsmail": teamsmail.strip().lower()
            }
 
            files = None
 
            if profile_picture is not None:
                files = {
                    "profile_picture": (
                        profile_picture.name,
                        profile_picture.getvalue(),
                        profile_picture.type
                    )
                }
 
            try:
 
                with st.spinner("Registering employee..."):
 
                    response = requests.post(
                        BACKEND_URL,
                        data=payload,
                        files=files,
                        timeout=30
                    )
 
                result = response.json()
 
                if response.status_code in [200, 201]:
 
                    st.success(result["message"])

 
                    st.session_state.page = "login"
                    st.rerun()
 
                else:
                    st.error(result.get("detail", "Registration failed."))
 
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend.")
 
            except requests.exceptions.Timeout:
                st.error("Request timed out.")
 
            except ValueError:
                st.error("Invalid response received from backend.")
 
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
if __name__ == "__main__":
    register()
 