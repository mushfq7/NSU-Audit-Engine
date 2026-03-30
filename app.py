import streamlit as st
import pandas as pd
import os
import datetime
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from PIL import Image
import scanner  

# --- CORE UI CONFIG (Must be first) ---
st.set_page_config(page_title="NSU Audit Portal", page_icon="🎓", layout="wide")

# --- SECURITY OVERRIDE FOR LOCALHOST ---
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# --- SESSION MEMORY (Must be at top) ---
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'scan_data' not in st.session_state:
    st.session_state.scan_data = None
if 'scan_filename' not in st.session_state:
    st.session_state.scan_filename = None

# --- EMAIL FUNCTION ---
def send_transcript_email(receiver_email, csv_file_path):
    sender_email = "mushfq7@gmail.com" 
    password = st.secrets["GMAIL_PASSWORD"] 
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "🎓 Your NSU Degree Audit Transcript"

    body = f"Hello!\n\nPlease find your scanned academic transcript attached.\n\nSent via NSU Audit Engine for {receiver_email}."
    message.attach(MIMEText(body, "plain"))

    with open(csv_file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=NSU_Transcript_Audit.csv")
        message.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

# --- FIREBASE CLOUD SETUP ---
if not os.path.exists("firebase_key.json") and "FIREBASE_JSON" in st.secrets:
    with open("firebase_key.json", "w") as f:
        f.write(st.secrets["FIREBASE_JSON"])

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

def get_flow():
    scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]
    secret_data = st.secrets["GOOGLE_JSON"]
    if isinstance(secret_data, str):
        client_config = json.loads(secret_data)
    else:
        client_config = dict(secret_data)
        
    flow = Flow.from_client_config(
        client_config,
        scopes=scopes,
        redirect_uri="https://nsu-audit-engine-5godskzpjon9ovconrxvzk.streamlit.app/"
    )
    return flow

# --- LOGIN INTERCEPTOR ---
if 'code' in st.query_params:
    try:
        if not os.path.exists(".auth_cache.json"):
            st.error("🚨 Authentication cache not found. Please clear the URL and click Login again.")
            st.stop()

        with open(".auth_cache.json", "r") as f:
            auth_data = json.load(f)

        flow = get_flow()
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
    
    flow = get_flow()
    auth_url, state = flow.authorization_url(prompt='select_account')
    
    with open(".auth_cache.json", "w") as f:
        json.dump({"state": state, "verifier": flow.code_verifier}, f)
    
    st.markdown(f'<br><a href="{auth_url}" target="_top" style="display: inline-block; padding: 12px 24px; background-color: #4285F4; color: white; text-decoration: none; font-size: 16px; border-radius: 5px; font-weight: bold; border: 1px solid #357AE8; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">🛡️ Sign in with Google</a>', unsafe_allow_html=True)

else:
    # 🔓 LOGGED IN VIEW
    col_header1, col_header2 = st.columns([4, 1])
    with col_header1:
        st.title("🏛️ NSU Enterprise Degree Audit")
    with col_header2:
        st.success(f"👤 {st.session_state.user_email}")
        if st.button("Logout"):
            st.session_state.user_email = None
            st.session_state.scan_data = None  # Clear data on logout
            st.rerun()

    st.markdown("Upload your official NSU transcript. Scans are automatically backed up to the secure cloud under your identity.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📥 Upload Transcript")
        uploaded_file = st.file_uploader("Drop Transcript Image (PNG/JPG) or CSV here", type=['png', 'jpg', 'jpeg', 'csv'])

        # --- 1. THE CAPTURE ENGINE ---
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
                            # Lock into memory
                            st.session_state.scan_filename = csv_filename
                            st.session_state.scan_data = pd.read_csv(csv_filename)
                            st.success("✅ OCR Extraction Successful!")
                            
                            # Push to Firebase
                            if db is not None:
                                records = st.session_state.scan_data.to_dict(orient='records')
                                doc_ref = db.collection('scan_history').document()
                                doc_ref.set({
                                    'timestamp': datetime.datetime.now(),
                                    'filename': uploaded_file.name,
                                    'user_account': st.session_state.user_email, 
                                    'total_courses_found': len(records),
                                    'data': records
                                })
                                st.toast("☁️ Scan safely backed up to Firebase!")
                        else:
                            st.error("⚠️ OCR failed to find recognizable courses.")
                    except Exception as e:
                        st.error(f"System Error: {e}")

            elif uploaded_file.type == 'text/csv':
                df = pd.read_csv(uploaded_file)
                st.session_state.scan_data = df
                st.session_state.scan_filename = "uploaded_data.csv"
                st.success("✅ CSV Database Loaded.")

        # --- 2. THE PERSISTENT DISPLAY AREA (With Email Button) ---
        if st.session_state.scan_data is not None:
            st.markdown("---")
            st.subheader("📊 Extracted Academic Records")
            
            # Email Button placed above the table for easy access
            if st.button("📧 Email Transcript to Me", type="primary"):
                with st.spinner("Sending email..."):
                    try:
                        temp_email_file = "transcript_to_send.csv"
                        st.session_state.scan_data.to_csv(temp_email_file, index=False)
                        send_transcript_email(st.session_state.user_email, temp_email_file)
                        st.success(f"Sent successfully to {st.session_state.user_email}!")
                    except Exception as e:
                        st.error(f"Email failed: {e}")
            
            # The Data Table
            st.dataframe(st.session_state.scan_data, use_container_width=True)

    with col2:
        st.markdown("### ☁️ Cloud History")
        st.markdown("Recent system-wide scans:")
        
        if st.button("Refresh Cloud History", type="secondary"):
            if db is not None:
                try:
                    history_ref = db.collection('scan_history').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5)
                    docs = history_ref.stream()
                    
                    found_history = False
                    for doc in docs:
                        found_history = True
                        record = doc.to_dict()
                        time_str = record['timestamp'].strftime("%Y-%m-%d %H:%M")
                        st.info(f"📄 **{record['filename']}**\n\n👤 {record['user_account']}\n\n⏱️ {time_str}\n\n📊 Courses: {record['total_courses_found']}")
                        
                    if not found_history:
                        st.warning("No scan history found yet.")
                except Exception as e:
                    st.error(f"Cloud Error: {e}")
            else:
                st.error("Firebase connection is not active.")