import os
import streamlit as st
import pandas as pd
import random
import re
import difflib

# ----------------- APP SETUP -----------------
st.set_page_config(page_title="German Learning App", page_icon="🇩🇪", layout="centered")
st.title("🔐 German Learning App Login")

# ----------------- LOGIN -----------------
# Load student codes from CSV or XLSX
codes_file_csv = "student_codes.csv"
codes_file_xlsx = "student_codes.xlsx"
if os.path.exists(codes_file_csv):
    codes_df = pd.read_csv(codes_file_csv)
elif os.path.exists(codes_file_xlsx):
    codes_df = pd.read_excel(codes_file_xlsx)
else:
    st.error(f"❗ '{codes_file_csv}' or '{codes_file_xlsx}' file missing.")
    st.stop()

# Normalize columns and extract valid codes
codes_df.columns = codes_df.columns.str.strip().str.lower()
if "code" not in codes_df.columns:
    st.error("❗ 'code' column missing in student codes file.")
    st.stop()
valid_codes = set(codes_df["code"].astype(str).str.strip().str.lower())

# Prompt for student code
student_code = st.text_input(
    "Enter your student code (if you don't have one contact your tutor):"
).strip().lower()

if not student_code:
    st.stop()

if student_code not in valid_codes:
    st.warning("Access denied. Please enter a valid code.")
    st.stop()

st.success(f"✅ Welcome, {student_code}!")

# ----------------- SCHOOL CONFIG -----------------
SCHOOL_NAME = "Learn Language Education Academy"

# ----------------- DASHBOARD -----------------
st.markdown(f"## 🏫 {SCHOOL_NAME}")
st.markdown(f"Welcome **{student_code}**! 👋")

st.markdown("---")
st.subheader("📌 Available Modules")

cols = st.columns(2)
with cols[0]:
    if st.button("📚 Start Vocabulary Quiz"):
        st.session_state["section_override"] = "📚 Vocabulary Quiz"
    if st.button("🧪 Start Grammar Quiz"):
        st.session_state["section_override"] = "🧪 Grammar Quiz"
with cols[1]:
    if st.button("✍️ Start Sentence Trainer"):
        st.session_state["section_override"] = "✍️ Sentence Trainer"
    if st.button("🔢 Start Grammar Practice"):
        st.session_state["section_override"] = "🔢 Grammar Practice"

# ----------------- SIDEBAR NAVIGATION -----------------
st.sidebar.title("🇩🇪 German Training Center")
level = st.sidebar.selectbox("Select your level:", ["A1", "A2"])

# Smart section selection (override buttons take priority)
if "section_override" not in st.session_state:
    if level == "A1":
        section = st.sidebar.radio("Choose a topic:", [
            "📚 Vocabulary Quiz",
            "✍️ Sentence Trainer",
            "🔢 Grammar Practice"
        ])
    else:
        section = st.sidebar.radio("Choose a topic:", [
            "📚 Vocabulary Quiz",
            "✍️ Sentence Trainer",
            "🧪 Grammar Quiz",
            "🔢 Grammar Practice"
        ])
else:
    section = st.session_state.pop("section_override")

# ----------------- VOCABULARY LISTS -----------------
# A1 and A2 vocabularies remain unchanged (omitted here for brevity)
# Insert your a1_vocab and a2_vocab definitions here

# ----------------- VOCABULARY QUIZ -----------------
# ... rest of the app code remains the same as before ...
# Ensure that session state keys are unique and that all control flow branches
# correctly call st.rerun() after state changes.

# (Due to length, the full sections for Vocabulary Quiz, Sentence Trainer,
# Grammar Practice, and Grammar Quiz are unchanged except for the file loading
# fix above.)
