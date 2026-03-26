import streamlit as st
import pandas as pd
import os
import datetime
import json
# --- CLOUD DEPLOYMENT SECRETS HACK ---
# If the app is running in the cloud, it won't find the physical JSON files.
# This code grabs the secret text from Streamlit's secure vault and recreates the files temporarily.
if not os.path.exists("firebase_key.json") and "FIREBASE_JSON" in st.secrets:
    with open("firebase_key.json", "w") as f:
        f.write(st.secrets["FIREBASE_JSON"])

if not os.path.exists("google_credentials.json") and "GOOGLE_JSON" in st.secrets:
    with open("google_credentials.json", "w") as f:
        f.write(st.secrets["GOOGLE_JSON"])
from PIL import Image
import scanner  

# --- CORE UI CONFIG (Must be first) ---
st.set_page_config(page_title="NSU Audit Portal", page_icon="🎓", layout="wide")

# --- SECURITY OVERRIDE FOR LOCALHOST ---
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# --- FIREBASE CLOUD SETUP ---
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    except FileNotFoundError:
        st.error("🚨 CRITICAL: 'firebase_key.json' not found.")
try:
    db = firestore.client()
except Exception:
    db = None

# --- GOOGLE AUTH SETUP ---
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

CLIENT_SECRETS_FILE = "google_credentials.json"
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']

def get_flow(state=None):
   flow = Flow.from_client_secrets_file(
    "google_credentials.json",
    scopes=scopes,
    redirect_uri="https://p4ejb.streamlit.app/"
)
    flow.redirect_uri = REDIRECT_URI
    return flow

# --- SESSION MEMORY ---
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# --- LOGIN INTERCEPTOR (Reads from Hard Drive) ---
if 'code' in st.query_params:
    try:
        # Check if our hidden cache file exists
        if not os.path.exists(".auth_cache.json"):
            st.error("🚨 Authentication cache not found. Please clear the URL and click Login again.")
            st.stop()

        # Read the saved passwords from the hard drive
        with open(".auth_cache.json", "r") as f:
            auth_data = json.load(f)

        flow = get_flow(state=auth_data["state"])
        
        # Inject the verifier from the file
        flow.fetch_token(
            code=st.query_params['code'],
            code_verifier=auth_data["verifier"]
        )
        
        creds = flow.credentials
        request = google_requests.Request()
        user_info = id_token.verify_oauth2_token(
            creds.id_token, request, flow.client_config['client_id']
        )
        
        st.session_state.user_email = user_info.get('email')
        
        # Clean up: Delete the temporary security file and clear the URL
        os.remove(".auth_cache.json")
        st.query_params.clear() 
        st.rerun() 
    except Exception as e:
        st.error(f"Authentication failed: {e}")

# ==========================================
#              THE USER INTERFACE
# ==========================================

if st.session_state.user_email is None:
    # 🔒 LOGGED OUT VIEW
    st.title("🏛️ NSU Enterprise Degree Audit")
    st.markdown("### Secure Identity Access Management (IAM)")
    st.info("System access restricted. Please authenticate with your Google account.")
    
    # Generate the secure URL
    flow = get_flow()
    auth_url, state = flow.authorization_url(prompt='consent')
    
    # THE FIX: Save the exact state and verifier to the hard drive
    with open(".auth_cache.json", "w") as f:
        json.dump({"state": state, "verifier": flow.code_verifier}, f)
    
    st.markdown(f'<br><a href="{auth_url}" target="_self" style="display: inline-block; padding: 12px 24px; background-color: #4285F4; color: white; text-decoration: none; font-size: 16px; border-radius: 5px; font-weight: bold; border: 1px solid #357AE8; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">🛡️ Sign in with Google</a>', unsafe_allow_html=True)

else:
    # 🔓 LOGGED IN VIEW
    col_header1, col_header2 = st.columns([4, 1])
    with col_header1:
        st.title("🏛️ NSU Enterprise Degree Audit")
    with col_header2:
        st.success(f"👤 {st.session_state.user_email}")
        if st.button("Logout"):
            st.session_state.user_email = None
            st.rerun()

    st.markdown("Upload your official NSU transcript. Scans are automatically backed up to the secure cloud under your identity.")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader("Drop Transcript Image (PNG/JPG) or CSV here", type=['png', 'jpg', 'jpeg', 'csv'])

        if uploaded_file is not None:
            if uploaded_file.type in ['image/png', 'image/jpeg', 'image/jpg']:
                st.info("Scanning document with Optical Character Recognition...")
                
                temp_img_path = "temp_upload.png"
                with open(temp_img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                with st.spinner("Extracting academic records..."):
                    try:
                        csv_filename = scanner.scan_image(temp_img_path)
                        
                        if csv_filename and os.path.exists(csv_filename):
                            st.success("✅ OCR Extraction Successful!")
                            df = pd.read_csv(csv_filename)
                            st.dataframe(df, use_container_width=True)
                            
                            if db is not None:
                                records = df.to_dict(orient='records')
                                doc_ref = db.collection('scan_history').document()
                                doc_ref.set({
                                    'timestamp': datetime.datetime.now(),
                                    'filename': uploaded_file.name,
                                    'user_account': st.session_state.user_email, 
                                    'total_courses_found': len(records),
                                    'data': records
                                })
                                st.toast("☁️ Scan safely backed up to Firebase Cloud!")
                                
                        else:
                            st.error("⚠️ OCR failed to find recognizable courses. Please upload a clearer image.")
                    except Exception as e:
                        st.error(f"System Error: {e}")

            elif uploaded_file.type == 'text/csv':
                df = pd.read_csv(uploaded_file)
                st.success("✅ CSV Database Loaded Successfully.")
                st.dataframe(df, use_container_width=True)

    with col2:
        st.markdown("### ☁️ Cloud History")
        st.markdown("Recent system-wide scans:")
        
        if db is not None and st.button("Refresh Cloud History"):
            history_ref = db.collection('scan_history').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5)
            docs = history_ref.stream()
            
            found_history = False
            for doc in docs:
                found_history = True
                record = doc.to_dict()
                time_str = record['timestamp'].strftime("%Y-%m-%d %H:%M")
                st.info(f"📄 **{record['filename']}**\n\n👤 {record['user_account']}\n\n⏱️ {time_str}\n\n📊 Courses Extracted: {record['total_courses_found']}")
                
            if not found_history:
                st.write("No scan history found in the cloud yet.")