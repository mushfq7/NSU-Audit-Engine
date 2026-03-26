import sqlite3
import pandas as pd
import hashlib

DB_NAME = "nsu_audit.db"


def init_db():
    """Initialize the SQL Database with Users and Transcript tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 1. Users Table (Security)
    c.execute(
        """CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, full_name TEXT)"""
    )

    # 2. Transcripts Table (Persistence)
    c.execute(
        """CREATE TABLE IF NOT EXISTS transcripts
                 (student_id TEXT, course_code TEXT, grade TEXT, credits REAL, semester TEXT)"""
    )

    # Create Default Admin & Student (Password: nsu123)
    # In real life, we hash passwords. Here we simulate it.
    pwd_hash = hashlib.sha256("nsu123".encode()).hexdigest()

    try:
        c.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?)",
            ("admin", pwd_hash, "admin", "Registrar Office"),
        )
        c.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?)",
            ("mushfiq", pwd_hash, "student", "Mushfiq Rahman"),
        )
    except sqlite3.IntegrityError:
        pass  # Already exists

    conn.commit()
    conn.close()


def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute(
        "SELECT role, full_name FROM users WHERE username=? AND password=?",
        (username, pwd_hash),
    )
    user = c.fetchone()
    conn.close()
    return user


def save_transcript(student_id, df):
    conn = sqlite3.connect(DB_NAME)
    # Clear old data for this student first (Simple Overwrite logic)
    c = conn.cursor()
    c.execute("DELETE FROM transcripts WHERE student_id=?", (student_id,))

    for index, row in df.iterrows():
        c.execute(
            "INSERT INTO transcripts VALUES (?, ?, ?, ?, ?)",
            (student_id, row["Course"], row["Grade"], row["Credits"], row["Semester"]),
        )
    conn.commit()
    conn.close()


def get_transcript(student_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT * FROM transcripts WHERE student_id=?", conn, params=(student_id,)
    )
    conn.close()
    return df
