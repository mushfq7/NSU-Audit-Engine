import streamlit as st
import pandas as pd
import db_handler
import nsu_logic
import report_gen  # Reuse your existing PDF generator

# --- CONFIG ---
st.set_page_config(page_title="NSU ERP Portal", layout="wide", page_icon="🏛️")

# Initialize DB on first run
db_handler.init_db()

# --- SESSION STATE MANAGEMENT ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = None
    st.session_state["username"] = None

# --- AUTHENTICATION SCREEN ---
if not st.session_state["logged_in"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("North_South_University_Monogram.svg.png", width=150)
        st.title("NSU Student Information System (RDS)")
        st.markdown("### Secure Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = db_handler.login_user(username, password)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = user[0]
                st.session_state["username"] = username
                st.session_state["fullname"] = user[1]
                st.rerun()
            else:
                st.error("Invalid credentials. Try: mushfiq / nsu123")
    st.stop()  # Stop execution here if not logged in

# --- DASHBOARD (LOGGED IN) ---
st.sidebar.title(f"👤 {st.session_state['fullname']}")
st.sidebar.caption(f"Role: {st.session_state['user_role'].upper()}")
menu = st.sidebar.radio(
    "Navigation", ["Dashboard", "Advising Panel", "Update Transcript", "Logout"]
)

if menu == "Logout":
    st.session_state["logged_in"] = False
    st.rerun()

# --- 1. UPDATE TRANSCRIPT (PERSISTENCE LAYER) ---
if menu == "Update Transcript":
    st.header("📂 Update Academic Record")
    st.info("Uploaded data will be saved to the secure University Database.")

    uploaded_file = st.file_uploader("Upload CSV Transcript", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        # Check if CSV has correct columns
        required_cols = ["Course", "Grade", "Credits", "Semester"]
        if all(col in df.columns for col in required_cols):
            db_handler.save_transcript(st.session_state["username"], df)
            st.success("✅ Database Updated Successfully!")
        else:
            st.error(f"CSV format error. Required columns: {required_cols}")

# --- LOAD DATA FOR DASHBOARD & ADVISING ---
# Fetch from SQL Database
df_transcript = db_handler.get_transcript(st.session_state["username"])

if df_transcript.empty:
    st.warning(
        "No transcript data found. Please upload a CSV in the 'Update Transcript' section."
    )
    st.stop()

cgpa, earned_cr, passed_courses = nsu_logic.calculate_cgpa(df_transcript)

# --- 2. MAIN DASHBOARD ---
if menu == "Dashboard":
    st.title("🎓 Academic Overview")

    # Enterprise Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("CGPA", f"{cgpa:.2f}", delta="Provisional")
    m2.metric("Credits Completed", f"{earned_cr}", "Req: 130")
    m3.metric(
        "Standing",
        "Good" if cgpa >= 2.0 else "Probation",
        delta_color="normal" if cgpa >= 2.0 else "inverse",
    )
    m4.metric("Courses Passed", len(passed_courses))

    st.divider()

    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("Recent Activity")
        st.dataframe(df_transcript.tail(10), use_container_width=True)

    with c2:
        st.subheader("Performance Trend")
        # Visualizing Grades (Simple Count)
        grade_counts = df_transcript["grade"].value_counts()
        st.bar_chart(grade_counts)

    if st.button("🖨️ Download Official Transcript (PDF)"):
        # We pass empty list for deficiencies for this simple demo, or connect full logic
        pdf_path = report_gen.generate_pdf(
            st.session_state["fullname"], "BBA MIS", cgpa, earned_cr, 130, []
        )
        with open(pdf_path, "rb") as f:
            st.download_button("Download PDF", f, file_name="NSU_Official_Record.pdf")

# --- 3. INTELLIGENT ADVISING PANEL ---
if menu == "Advising Panel":
    st.title("🤖 AI Course Advisor")
    st.markdown(
        "The system analyzes your **passed courses** and **prerequisites** to suggest your next semester."
    )

    # Demo Program Structure (Ideally loaded from .md file)
    demo_courses = [
        "MIS210",
        "MIS310",
        "MIS320",
        "MIS470",
        "CSE215",
        "CSE225",
        "MAT120",
        "BUS498",
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Eligible Courses")
        st.markdown("You meet the prerequisites for:")

        eligible = nsu_logic.suggest_courses(passed_courses, demo_courses)

        for course in eligible:
            st.success(f"**{course}** - Ready to take")

    with col2:
        st.subheader("🚫 Locked Courses")
        st.markdown("You are missing requirements for:")

        for course in demo_courses:
            if course not in passed_courses and course not in eligible:
                status, reason = nsu_logic.check_prerequisites(course, passed_courses)
                st.error(f"**{course}**: {reason}")
