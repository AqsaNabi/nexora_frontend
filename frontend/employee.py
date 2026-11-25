import streamlit as st
import pandas as pd
import requests
from api import api_request, API_URL


def employee():
    col_back, col_refresh = st.columns([1, 5])
    with col_back:
        if st.button("← Back", type="primary", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    st.title("👥 Employee Directory")
    st.caption("View and manage all registered employees across the organization.")

    # Fetch total count and details
    total_count = None
    try:
        count_res = api_request("GET", "/count", timeout=10)
        if count_res.status_code == 200:
            total_count = count_res.json().get("count")
    except Exception:
        pass

    try:
        with st.spinner("Fetching employee records..."):
            response = api_request("GET", "/details", timeout=15)
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to backend server at {API_URL}. Please ensure it is running.")
        return
    except requests.exceptions.Timeout:
        st.error("Request timed out fetching employee records.")
        return
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return

    if response.status_code == 200:
        try:
            data = response.json()
        except ValueError:
            st.error("Invalid data received from backend.")
            return

        # Show metrics
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Total Employees", total_count if total_count is not None else len(data))

        if data and isinstance(data, list):
            df = pd.DataFrame(data)

            # Ensure all expected columns exist
            expected_cols = [
                "full_name",
                "email",
                "designation",
                "mobile",
                "teamsmail",
                "gender",
                "date_of_birth",
            ]
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = ""

            # Search / Filter
            search = st.text_input("🔍 Search employees (name, designation, email)", "")
            if search.strip():
                query = search.strip().lower()
                mask = (
                    df["full_name"].astype(str).str.lower().str.contains(query, na=False)
                    | df["designation"].astype(str).str.lower().str.contains(query, na=False)
                    | df["email"].astype(str).str.lower().str.contains(query, na=False)
                )
                display_df = df[mask]
            else:
                display_df = df

            # Display table
            st.dataframe(
                display_df[[
                    "full_name",
                    "designation",
                    "email",
                    "mobile",
                    "teamsmail",
                    "gender",
                    "date_of_birth",
                ]],
                use_container_width=True,
                hide_index=True,
                height=450,
                column_config={
                    "full_name": st.column_config.TextColumn(
                        "Employee Name",
                        width="medium",
                    ),
                    "designation": st.column_config.TextColumn(
                        "Designation",
                        width="medium",
                    ),
                    "email": st.column_config.TextColumn(
                        "Email Address",
                        width="large",
                    ),
                    "mobile": st.column_config.TextColumn(
                        "Mobile",
                        width="small",
                    ),
                    "teamsmail": st.column_config.TextColumn(
                        "Teams Email",
                        width="large",
                    ),
                    "gender": st.column_config.TextColumn(
                        "Gender",
                        width="small",
                    ),
                    "date_of_birth": st.column_config.TextColumn(
                        "Date of Birth",
                        width="small",
                    ),
                },
            )
            st.caption(f"Showing {len(display_df)} of {len(df)} employee records.")
        else:
            st.info("No employee records found in the database.")

    elif response.status_code == 401:
        st.warning("Your session has expired or is unauthorized. Please sign in again.")
        if st.button("Sign In"):
            st.session_state.page = "login"
            st.rerun()
    else:
        st.error(f"Unable to fetch employee details. (Status code {response.status_code})")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Nexora | Employee Directory",
        page_icon="👥",
        layout="wide",
    )
    employee()
