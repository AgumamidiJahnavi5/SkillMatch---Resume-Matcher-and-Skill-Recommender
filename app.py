import streamlit as st
import sqlite3
import bcrypt
import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- NLTK SETUP ----------------
nltk.download("stopwords")
from nltk.corpus import stopwords
STOP_WORDS = set(stopwords.words("english"))

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Resume Match & Skill Suggester",
    layout="wide"
)

# ---------------- DATABASE ----------------
def create_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password BLOB
        )
    """)
    conn.commit()
    conn.close()

create_db()

# ---------------- AUTH FUNCTIONS ----------------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

# ---------------- NLP FUNCTIONS ----------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS]
    return " ".join(words)

SKILL_LIST = [
    "python", "java", "sql", "html", "css", "javascript",
    "machine learning", "data analysis", "nlp",
    "tensorflow", "pytorch", "flask", "streamlit",
    "numpy", "pandas", "git"
]

def extract_skills(text):
    found = []
    for skill in SKILL_LIST:
        if skill in text:
            found.append(skill)
    return list(set(found))

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

# ---------------- SIDEBAR ----------------
st.sidebar.title("Menu")

if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Navigate", ["Login", "Register"])
else:
    menu = st.sidebar.radio("Navigate", ["Upload & Analyze", "Logout"])
    st.sidebar.success(f"User: {st.session_state.user_email}")

# ---------------- REGISTER ----------------
if menu == "Register":
    st.title("Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone():
            st.error("User already exists")
        else:
            c.execute(
                "INSERT INTO users VALUES (?, ?)",
                (email, hash_password(password))
            )
            conn.commit()
            st.success("Registration successful! Please login.")
        conn.close()

# ---------------- LOGIN ----------------
if menu == "Login":
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE email=?", (email,))
        result = c.fetchone()
        conn.close()

        if result and check_password(password, result[0]):
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------- LOGOUT ----------------
if menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.rerun()

# ---------------- MAIN APP ----------------
if menu == "Upload & Analyze" and st.session_state.logged_in:

    st.title("📄 Resume Match & Skill Suggester")

    st.subheader("Upload Resume & Job Description (TXT files)")
    resume_file = st.file_uploader("Upload Resume", type=["txt"])
    jd_file = st.file_uploader("Upload Job Description", type=["txt"])

    if resume_file and jd_file:
        resume_text = resume_file.read().decode("utf-8")
        jd_text = jd_file.read().decode("utf-8")

        # -------- CLEAN TEXT --------
        clean_resume = clean_text(resume_text)
        clean_jd = clean_text(jd_text)

        # -------- EXTRACT SKILLS --------
        resume_skills = extract_skills(clean_resume)
        jd_skills = extract_skills(clean_jd)

        matching_skills = list(set(resume_skills) & set(jd_skills))
        missing_skills = list(set(jd_skills) - set(resume_skills))

        # -------- MATCH SCORE --------
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([clean_resume, clean_jd])
        score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100

        # ---------------- OUTPUT ----------------
        st.markdown("## 📊 Analysis Results")

        col1, col2, col3 = st.columns(3)
        col1.metric("Match Score", f"{score:.0f}%")
        col2.metric("Matching Skills", len(matching_skills))
        col3.metric("Missing Skills", len(missing_skills))

        st.progress(int(score))

        st.markdown("### ✅ Extracted Resume Skills")
        st.write(resume_skills if resume_skills else "No skills detected")

        st.markdown("### 📌 Extracted Job Description Skills")
        st.write(jd_skills if jd_skills else "No skills detected")

        st.markdown("### 🟢 Matching Skills")
        st.write(matching_skills if matching_skills else "No matching skills")

        st.markdown("### 🔴 Missing Skills")
        st.write(missing_skills if missing_skills else "No missing skills 🎉")