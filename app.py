
import streamlit as st
import pandas as pd
import os
import random
import string
from datetime import datetime

# --- Initialize ---
st.set_page_config(page_title="Mentee Tracker", layout="wide")

# Create data folder if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

# --- Access Key Logic (simplified) ---
def generate_access_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_user_key(email_or_phone):
    key_file = "data/access_keys.csv"
    if not os.path.exists(key_file):
        df = pd.DataFrame(columns=["user", "key"])
        df.to_csv(key_file, index=False)
    df = pd.read_csv(key_file)
    if email_or_phone in df["user"].values:
        return df[df["user"] == email_or_phone]["key"].values[0]
    else:
        new_key = generate_access_key()
        new_row = pd.DataFrame([{"user": email_or_phone, "key": new_key}])
        new_row.to_csv(key_file, mode="a", header=False, index=False)
        return new_key

# --- Login Page ---
st.title("🔐 Mentee Tracker System")

role = st.radio("Login as", ["Student", "Mentor"], horizontal=True)

email = st.text_input("📧 Enter Email")
phone = st.text_input("📱 Enter Phone Number")

if email or phone:
    user_identifier = email if email else phone
    access_key = get_user_key(user_identifier)
    st.info(f"Your Access Key: `{access_key}`")

user_key_input = st.text_input("🔑 Enter your Access Key to Continue", type="password")

if user_key_input == access_key:
    st.success("Login successful ✅")

    tab1, tab2, tab3 = st.tabs(["🎓 Marks", "📅 Meetings", "🏆 Activity Points"])

    # -------------- MARKS TAB ----------------
    with tab1:
        st.header("🎓 Academic Marks Entry")

        # 🆕 Semester Dropdown
        semester = st.selectbox("📚 Select Semester", 
                                ["1st Sem", "2nd Sem", "3rd Sem", "4th Sem", 
                                 "5th Sem", "6th Sem", "7th Sem", "8th Sem"])

        subject_count = st.number_input("Number of Subjects", min_value=1, max_value=12, value=4)

        data = []
        grades = ["O", "A+", "A", "B+", "B", "C+", "C", "PP"]
        total_credits = 0
        weighted_score = 0

        for i in range(int(subject_count)):
            st.subheader(f"Subject {i+1}")
            subject = st.text_input(f"Subject Name {i+1}", key=f"sub{i}")
            mse1 = st.number_input(f"MSE 1 - {subject}", min_value=0, max_value=50, key=f"mse1{i}")
            mse2 = st.number_input(f"MSE 2 - {subject}", min_value=0, max_value=50, key=f"mse2{i}")
            see = st.number_input(f"SEE - {subject}", min_value=0, max_value=100, key=f"see{i}")
            task = st.number_input(f"Task - {subject}", min_value=0, max_value=20, key=f"task{i}")
            grade = st.selectbox(f"Grade - {subject}", grades, key=f"grade{i}")
            credit = st.number_input(f"Credits - {subject}", min_value=1, max_value=5, key=f"credit{i}")

            # Grade to point mapping
            grade_map = {
                "O": 10, "A+": 9, "A": 8, "B+": 7,
                "B": 6, "C+": 5, "C": 4, "PP": 0
            }
            grade_point = grade_map.get(grade, 0)
            weighted_score += grade_point * credit
            total_credits += credit

            data.append({
                "Email/Phone": user_identifier,
                "Semester": semester,
                "Subject": subject,
                "MSE1": mse1,
                "MSE2": mse2,
                "SEE": see,
                "Task": task,
                "Grade": grade,
                "Credits": credit
            })

        # Save data
        if st.button("💾 Save Marks"):
            df = pd.DataFrame(data)
            sem_filename = f"data/marks_{user_identifier}_{semester.replace(' ', '_')}.csv"
            file_exists = os.path.exists(sem_filename)
            df.to_csv(sem_filename, mode="a", index=False, header=not file_exists)
            st.success("Marks saved for this semester 🎉")

        # CGPA Calculation
        if total_credits > 0:
            cgpa = round(weighted_score / total_credits, 2)
            st.info(f"🎯 CGPA for {semester}: **{cgpa}**")
