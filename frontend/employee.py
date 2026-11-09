from api import api_request
import streamlit as st
import pandas as pd


def employee():
    if st.button("← Back"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.subheader("👥 Employee Details")
    st.caption("View and manage all registered employees.")

    response = api_request("GET", "/details")

    if response.status_code == 200:

        data = response.json()

        if data:

            df = pd.DataFrame(data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=450,
                column_config={
                    
                    "Name": st.column_config.TextColumn(
                        "Employee Name",
                        width="medium"
                    ),
                    "email": st.column_config.TextColumn(
                        "Email Address",
                        width="large"
                    ),
                    "phone": st.column_config.TextColumn(
                        "Phone Number"
                    ),
                    "role": st.column_config.TextColumn(
                        "Role"
                    ),
                    "department": st.column_config.TextColumn(
                        "Department"
                    )
                }
            )

        else:
            st.info("No employee records found.")

    else:
        st.error("Unable to fetch employee details.")