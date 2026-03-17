import streamlit as st
import sqlite3
import bcrypt
import nltk
import re
import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ---------------- NLTK ----------------
nltk.download("stopwords")
from nltk.corpus import stopwords
STOP_WORDS = set(stopwords.words("english"))

# ---------------- PAGE ----------------
st.set_page_config(page_title="Resume Match System", layout="wide")

# ---------------- DATABASE ----------------
def create_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password BLOB,
            role TEXT
        )
    """)
    conn.commit()
    conn.close()

create_db()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

# ---------------- NLP ----------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS]
    return " ".join(words)

# ---------------- SKILLS ----------------
if "skill_list" not in st.session_state:
    st.session_state.skill_list = [
        "python","java","sql","html","css","javascript",
        "machine learning","data analysis","nlp",
        "tensorflow","pytorch","flask","streamlit",
        "numpy","pandas","git"
    ]

def extract_skills(text):
    return list(set([s for s in st.session_state.skill_list if s in text]))

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- SIDEBAR ----------------
st.sidebar.title("Resume Match Dashboard")

if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])
else:
    menu = st.sidebar.radio("Navigation",
        ["Upload Files", "Matching Dashboard", "Suggestions",
         "Admin Panel", "Export Report", "Logout"]
    )

# ================= REGISTER =================
if menu == "Register":
    st.title("Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["user", "admin"])

    if st.button("Register"):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)",
                  (email, hash_password(password), role))
        conn.commit()
        conn.close()
        st.success("Registered Successfully")

# ================= LOGIN =================
if menu == "Login":
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT password, role FROM users WHERE email=?", (email,))
        result = c.fetchone()
        conn.close()

        if result and check_password(password, result[0]):
            st.session_state.logged_in = True
            st.session_state.role = result[1]
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ================= LOGOUT =================
if menu == "Logout":
    st.session_state.logged_in = False
    st.rerun()

# =====================================================
# ================== FILE UPLOAD ======================
# =====================================================
if menu == "Upload Files" and st.session_state.logged_in:

    st.title("Upload Resume & Job Description")

    resume_file = st.file_uploader("Upload Resume (.txt)", type=["txt"])
    jd_file = st.file_uploader("Upload Job Description (.txt)", type=["txt"])

    if resume_file and jd_file:

        resume_text = resume_file.read().decode("utf-8")
        jd_text = jd_file.read().decode("utf-8")

        clean_resume = clean_text(resume_text)
        clean_jd = clean_text(jd_text)

        st.session_state.resume_clean = clean_resume
        st.session_state.jd_clean = clean_jd
        st.session_state.resume_skills = extract_skills(clean_resume)
        st.session_state.jd_skills = extract_skills(clean_jd)

        st.success("Files Processed Successfully!")

# =====================================================
# ================= MATCHING DASHBOARD =================
# =====================================================
if menu == "Matching Dashboard" and st.session_state.logged_in:

    if "resume_clean" not in st.session_state:
        st.warning("Upload files first.")
    else:
        st.title("Matching Dashboard")

        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(
            [st.session_state.resume_clean, st.session_state.jd_clean]
        )
        score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100

        matching = list(set(st.session_state.resume_skills)
                        & set(st.session_state.jd_skills))
        missing = list(set(st.session_state.jd_skills)
                       - set(st.session_state.resume_skills))

        st.session_state.score = score
        st.session_state.matching = matching
        st.session_state.missing = missing

        # Donut Chart
        fig = go.Figure(go.Pie(
            values=[score, 100-score],
            hole=0.6
        ))
        fig.update_layout(title="Match Percentage")
        st.plotly_chart(fig)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Matched Skills")
            for skill in matching:
                st.success(skill)

        with col2:
            st.subheader("Missing Skills")
            for skill in missing:
                st.error(skill)

# =====================================================
# ================== SUGGESTIONS ======================
# =====================================================
if menu == "Suggestions" and st.session_state.logged_in:

    st.title("Skill Suggestions")

    if "missing" not in st.session_state:
        st.warning("Run Matching First")
    else:
        for skill in st.session_state.missing:
            st.info(f"Recommended to Learn: {skill}")

# =====================================================
# ================== ADMIN PANEL ======================
# =====================================================
if menu == "Admin Panel" and st.session_state.logged_in:

    if st.session_state.role != "admin":
        st.error("Access Denied (Admin Only)")
    else:
        st.title("Admin Dashboard - Manage Skills")

        new_skill = st.text_input("Add New Skill")
        if st.button("Add Skill"):
            st.session_state.skill_list.append(new_skill.lower())
            st.success("Skill Added")

        st.subheader("Current Skills")
        st.write(st.session_state.skill_list)

# =====================================================
# ================= EXPORT REPORT =====================
# =====================================================
if menu == "Export Report" and st.session_state.logged_in:

    if "score" not in st.session_state:
        st.warning("Run Matching First")
    else:
        doc = SimpleDocTemplate("Resume_Report.pdf", pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Resume Match Report", styles["Title"]))
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(f"Match Score: {st.session_state.score:.2f}%", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(f"Matched Skills: {', '.join(st.session_state.matching)}", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(f"Missing Skills: {', '.join(st.session_state.missing)}", styles["Normal"]))

        doc.build(elements)

        with open("Resume_Report.pdf", "rb") as f:
            st.download_button("Download Report", f, file_name="Resume_Report.pdf")

        st.success("Report Ready!")
