import json
import queue
import threading
import time
import urllib.parse  # <--- ADDED THIS
 
import websocket
from requests.exceptions import RequestException
 
from api import api_request
 
 
# =========================================================
# CONFIGURATION
# =========================================================
 
API_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 30
 
WS_URL = "ws://127.0.0.1:8000/ws/ats/notifications"
 
 
# =========================================================
# WEBSOCKET CONFIGURATION
# =========================================================
 
notification_queue = queue.Queue()
 
websocket_thread = None
websocket_lock = threading.Lock()
 
 
# =========================================================
# 1. FETCH DASHBOARD DATA
# =========================================================
 
def fetch_dashboard_data():
 
    try:
 
        response = api_request(
            "get",
            "/api/ats/dashboard",
            timeout=REQUEST_TIMEOUT
        )
 
        response.raise_for_status()
 
        return response.json(), None
 
    except RequestException as error:
 
        return None, str(error)
 
    except ValueError:
 
        return None, "Dashboard API returned an invalid JSON response."
 
 
# =========================================================
# 2. FETCH APPLICATIONS FOR A JOB
# =========================================================
 
def fetch_applications(post_id):
 
    try:
 
        response = api_request(
            "get",
            f"/api/ats/jobs/{post_id}/applications",
            timeout=REQUEST_TIMEOUT
        )
 
        response.raise_for_status()
 
        return response.json(), None
 
    except RequestException as error:
 
        return None, str(error)
 
    except ValueError:
 
        return None, "Applications API returned an invalid JSON response."
 
 
# =========================================================
# 3. SUBMIT APPLICATION
# =========================================================
 
def submit_application(post_id, application_data):
 
    try:
 
        response = api_request(
            "post",
            f"/api/ats/jobs/{post_id}/applications",
            json=application_data,
            timeout=REQUEST_TIMEOUT
        )
 
        response.raise_for_status()
 
        return response.json(), None
 
    except RequestException as error:
 
        return None, str(error)
 
    except ValueError:
 
        return None, "Application API returned an invalid JSON response."
 
 
# =========================================================
# 4. WEBSOCKET LISTENER
# =========================================================
 
def websocket_listener(token):
 
    while True:
 
        try:
 
            def on_message(ws, message):
 
                try:
 
                    notification = json.loads(message)
 
                    if isinstance(notification, dict):
 
                        notification_queue.put(notification)
 
                except json.JSONDecodeError:
 
                    print("Invalid WebSocket notification received.")
 
            def on_error(ws, error):
 
                print("WebSocket error:", error)
 
            def on_close(ws, close_status_code, close_msg):
 
                print("ATS WebSocket disconnected.")
 
            def on_open(ws):
 
                print("ATS WebSocket connected.")
 
            # --- CHANGED THIS SECTION ---
            # Append the token to the URL
            safe_token = urllib.parse.quote(token) if token else ""
            full_ws_url = f"{WS_URL}?token={safe_token}"

            ws = websocket.WebSocketApp(
                full_ws_url,   # <--- using the URL with the token now
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            # ----------------------------
 
            ws.run_forever(
                ping_interval=20,
                ping_timeout=10
            )
 
        except Exception as error:
 
            print("WebSocket connection error:", error)
 
        time.sleep(5)
 
 
# =========================================================
# 5. START WEBSOCKET
# =========================================================
 
def start_websocket(token):  # <--- CHANGED: now accepts token
 
    global websocket_thread
 
    with websocket_lock:
 
        if (
            websocket_thread is not None
            and websocket_thread.is_alive()
        ):
 
            return
 
        # Pass the token to the listener thread
        websocket_thread = threading.Thread(
            target=websocket_listener,
            args=(token,),  # <--- CHANGED: passing token in
            daemon=True
        )
 
        websocket_thread.start()
