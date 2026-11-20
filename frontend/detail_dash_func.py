import requests
 
 
# =========================================================
# CONFIGURATION
# =========================================================
 
API_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 30
 
 
# =========================================================
# 1. FETCH DASHBOARD DATA
# =========================================================
 
def fetch_dashboard_data():
 
    try:
        response = requests.get(
            f"{API_URL}/api/ats/dashboard",
            timeout=REQUEST_TIMEOUT
        )
 
        response.raise_for_status()
 
        return response.json(), None
 
    except requests.exceptions.RequestException as error:
        return None, str(error)
 
    except ValueError:
        return None, "Dashboard API returned an invalid JSON response."
 
 
# =========================================================
# 2. FETCH APPLICATIONS FOR A JOB
# =========================================================
 
def fetch_applications(post_id):
 
    try:
        response = requests.get(
            f"{API_URL}/api/ats/jobs/{post_id}/applications",
            timeout=REQUEST_TIMEOUT
        )
 
        response.raise_for_status()
 
        return response.json(), None
 
    except requests.exceptions.RequestException as error:
        return None, str(error)
 
    except ValueError:
        return None, "Applications API returned an invalid JSON response."
 
 
# =========================================================
# 3. SUBMIT APPLICATION
# =========================================================
 
def submit_application(post_id, application_data):
 
    try:
        response = requests.post(
            f"{API_URL}/api/ats/jobs/{post_id}/applications",
            json=application_data,
            timeout=REQUEST_TIMEOUT
        )
 
        response.raise_for_status()
 
        return response.json(), None
 
    except requests.exceptions.RequestException as error:
        return None, str(error)
 
    except ValueError:
        return None, "Application API returned an invalid JSON response."
 
 
